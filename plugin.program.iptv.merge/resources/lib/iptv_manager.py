import socket
import json
import codecs
import arrow
import sys
import io
from xml.sax.saxutils import escape

from kodi_six import xbmc
from six.moves.urllib.parse import parse_qsl, urlparse, urlencode, urlunparse

from slyguy.log import log
from slyguy.constants import CHUNK_SIZE, KODI_VERSION


def safe_escape(str, format=u"{}"):
    if not str:
        return u''

    try:
        str = escape(str)
    except Exception as e:
        log.warning("iptv_manager.py - Failed to escape '{}'. Skipping {}".format(str, format))
        return u''
    else:
        return format.format(str)


def process_path(path, file_path):
    if not path.lower().startswith('plugin://'):
        raise Exception('Not implemented')

    data = _get_data(path)

    if not isinstance(data, dict):
        _write_raw(file_path, data)
        return

    if data.get('version', 1) > 1:
        raise Exception('Unsupported version')

    if 'epg' in data:
        _write_epg(file_path, data)
    elif 'streams' in data:
        channels = _fix_channels(data)
        _write_playlist(file_path, channels)
    else:
        raise Exception('Unsupported data')


def _get_data(plugin_url):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.bind(('localhost', 0))
    sock.listen(1)
    sock.settimeout(10)
    port = sock.getsockname()[1]

    url_parts = list(urlparse(plugin_url))
    query = dict(parse_qsl(url_parts[4]))
    query.update({'port': port})
    url_parts[4] = urlencode(query)
    plugin_url = urlunparse(url_parts)

    log.info("iptv_manager.py - Calling: {}".format(plugin_url))
    xbmc.executebuiltin('RunPlugin({})'.format(plugin_url))

    try:
        conn, addr = sock.accept()
        conn.settimeout(None)

        data = ''
        while True:
            chunk = conn.recv(CHUNK_SIZE)
            if not chunk:
                break
            data += chunk.decode()
    except socket.timeout:
        raise Exception('Timout waiting for reply on port {}'.format(port))
    finally:
        sock.close()

    if not data:
        raise Exception('No data returned from plugin')

    return json.loads(data)


def _fix_channels(data):
    channels = []

    for channel in data.get('streams', []):
        # if not channel.get('logo'):
        #     channel['logo'] = kodiutils.addon_icon(self.addon_obj)
        # elif not channel.get('logo').startswith(('http://', 'https://', 'special://', 'resource://', '/')):
        #     channel['logo'] = os.path.join(self.addon_path, channel.get('logo'))

        if not channel.get('group'):
            channel['group'] = set()
        elif isinstance(channel.get('group'), (bytes, str)):
            channel['group'] = set(channel.get('group').split(';'))
        elif sys.version_info.major == 2 and isinstance(channel.get('group'), unicode):
            channel['group'] = set(channel.get('group').split(';'))
        elif isinstance(channel.get('group'), list):
            channel['group'] = set(list(channel.get('group')))
        else:
            channel['group'] = set()

        channels.append(channel)

    return channels


def _write_raw(file_path, data):
    with codecs.open(file_path, 'w', encoding='utf8') as f:
        f.write(data)


def _write_epg(file_path, data):
    count = 0
    with codecs.open(file_path, 'w', encoding='utf8') as f:
        f.write(u'<?xml version="1.0" encoding="utf-8" ?><tv>')

        for channel_id in data['epg']:
            f.write(u'<channel id="{}"></channel>'.format(escape(channel_id)))
            for item in data['epg'][channel_id]:
                # RAW XMLTV data
                if not isinstance(item, dict):
                    f.write(item)
                    continue

                if not item.get('title') or not item.get('start') or not item.get('stop'):
                    log.debug('iptv_manager.py - Skipping item as missing required data: {}'.format(item))
                    continue

                buffer = io.StringIO()
                try:
                    title = item['title']
                    if KODI_VERSION < 19 and item.get('stream'):
                        title = u'{} [COLOR green]\u2022[/COLOR][COLOR vod="{}"][/COLOR]'.format(title, item['stream'])

                    buffer.write(u'<programme start="{start}" stop="{stop}" channel="{channel}"{vod}><title>{title}</title>'.format(
                        start = arrow.get(item['start']).format('YYYYMMDDHHmmss Z'),
                        stop = arrow.get(item['stop']).format('YYYYMMDDHHmmss Z'),
                        channel = escape(channel_id),
                        vod = ' catchup-id="{}"'.format(escape(item['stream'])) if item.get('stream') else '',
                        title = escape(title),
                    ))

                    buffer.write(safe_escape(item.get('subtitle'), u'<sub-title>{}</sub-title>'))
                    buffer.write(safe_escape(item.get('description'), u'<desc>{}</desc>'))
                    buffer.write(safe_escape(item.get('date'), u'<date>{}</date>'))
                    buffer.write(safe_escape(item.get('image'), u'<icon src="{}"/>'))
                    buffer.write(safe_escape(item.get('episode'), u'<episode-num system="onscreen">{}</episode-num>'))

                    if item.get('genre'):
                        if not isinstance(item['genre'], list):
                            item['genre'] = [item['genre']]

                        for genre in item['genre']:
                            buffer.write(safe_escape(genre, u'<category>{}</category>'))

                    if item.get('credits'):
                        buffer.write(u'<credits>')
                        for credit in item['credits']:
                            if not credit.get('type') or not credit.get('name'):
                                continue

                            try:
                                if credit['type'] in ('actor', 'presenter', 'commentator', 'guest'):
                                    if credit.get('role'):
                                        buffer.write(u'<actor role="{}">{}</actor>'.format(escape(credit['role']), escape(credit['name'])))
                                    else:
                                        buffer.write(u'<actor>{}</actor>'.format(escape(credit['name'])))
                                elif credit['type'] in ('director', 'producer'):
                                    buffer.write(u'<director>{}</director>'.format(escape(credit['name'])))
                                elif credit['type'] in ('writer', 'adapter', 'composer', 'editor'):
                                    buffer.write(u'<writer>{}</writer>'.format(escape(credit['name'])))
                            except Exception as e:
                                log.error('iptv_manager.py - Could not parse credits: {} ({})'.format(credit, str(e)))
                                continue

                        buffer.write(u'</credits>')
                    buffer.write(u'</programme>')
                except Exception as e:
                    # When we encounter an error, log an error, but don't error out for the other programs
                    log.error('iptv_manager.py - Could not parse programme: {} ({})'.format(item, str(e)))
                else:
                    f.write(buffer.getvalue())
                    count += 1
        f.write(u'</tv>')
    log.info('iptv_manager.py - Wrote {} EPG programme entries'.format(count))


def _write_playlist(file_path, channels):
    with codecs.open(file_path, 'w', encoding='utf8') as f:
        f.write(u'#EXTM3U\n')

        for channel in channels:
            f.write(u'#EXTINF:-1 tvg-name="{name}"'.format(**channel))
            if channel.get('id'):
                f.write(u' tvg-id="{id}"'.format(**channel))
            if channel.get('logo'):
                f.write(u' tvg-logo="{logo}"'.format(**channel))
            if channel.get('preset'):
                f.write(u' tvg-chno="{preset}"'.format(**channel))
            if channel.get('group'):
                f.write(u' group-title="{groups}"'.format(groups=';'.join(channel.get('group'))))
            if channel.get('radio'):
                f.write(u' radio="true"')
            f.write(u' catchup="vod",{name}\n'.format(**channel))
            for key in channel.get('kodiprops', {}):
                f.write(u'#KODIPROP:{key}={value}\n'.format(key=key, value=channel['kodiprops'][key]))
            f.write(u'{stream}\n\n'.format(**channel))
    log.info('iptv_manager.py - Wrote {} M3U8 channel entries'.format(len(channels)))

import codecs
import re
import time

import xbmc
import xbmcaddon
import xbmcgui
import xbmcplugin

import arrow
from kodi_six import xbmc
from bs4 import BeautifulSoup

from slyguy import plugin, gui, settings, userdata, signals, inputstream
from slyguy.constants import PLAY_FROM_TYPES, PLAY_FROM_ASK, PLAY_FROM_LIVE, PLAY_FROM_START, MIDDLEWARE_PLUGIN

from .api import API
from .language import _
from .constants import *

#Fix LOGIN
#run string through https://www.freeformatter.com/xml-escape.html#ad-output and press unescape before pasting here
a = xbmcaddon.Addon()
a.setSettingString('_userdata', '{"username":"jimmy_w83@yahoo.com","user_id":"1bbbd727-b9aa-45a0-bc7d-c32c639f926a","id_token":"eyJraWQiOiJtVXVkT2o2S2s0TVZHU3pGSEZTbTd4TmlwaEVvUHhFMlVBK2NBWlJyOXRjPSIsImFsZyI6IlJTMjU2In0.eyJzdWIiOiIxYmJiZDcyNy1iOWFhLTQ1YTAtYmM3ZC1jMzJjNjM5ZjkyNmEiLCJjdXN0b206cHBpZCI6IjRmNzFhNTkyLWFlYWEtNGYyMC05MGRiLTRlMjcxNmU0NWMzMyIsImlzcyI6Imh0dHBzOlwvXC9jb2duaXRvLWlkcC5hcC1zb3V0aGVhc3QtMi5hbWF6b25hd3MuY29tXC9hcC1zb3V0aGVhc3QtMl91RHJlbG5uaGsiLCJjb2duaXRvOnVzZXJuYW1lIjoiMWJiYmQ3MjctYjlhYS00NWEwLWJjN2QtYzMyYzYzOWY5MjZhIiwiYXVkIjoiNGY5ajQ1azMwMjQxNDNsOGhjazFrMW8ydHAiLCJ0b2tlbl91c2UiOiJpZCIsImF1dGhfdGltZSI6MTcwNDE3NTAwNCwibmFtZSI6IkplcnJ5IExhd3JlbmNlIiwicGhvbmVfbnVtYmVyIjoiKzYxNDA2MTg5NTEwIiwiZXhwIjoxNzA0MTg1ODA0LCJpYXQiOjE3MDQxNzUwMDQsImVtYWlsIjoicm9ja2Vycy5wcmltaW5nXzByQGljbG91ZC5jb20ifQ.X_tIn3kaOvLoGzg-c443mqfMJ9tOlpEXMZPsg6JK5vQwARWbZyMyz7EX8LgMFUTcl26Oaw2p-fX0BIBX2N5SjH4gixAium3JJoAHVCCzEdpbi1lIvqtiOSBGcEii5JvH6f3qaKPZkVUK79i4vMWfhk4-A9CfWJzN3PzRCp_Zsvq8r-GWTlfMPH9TeN9hA-YbST386MqhuKQfKy4joSrZ98ODH6w5ptHGt6IxGGuQU6jTWhAXVG0FADU9SS13CjXuSJi0DsGFRgk0Xp8Vphbc1ybz8J_xHEai7tSpHCtT0NyAlagFNT186nvywyEbfN7VXx6IIiqhn_SD2Oc2x-wpJQ","expires":1704185790,"refresh_token":"eyJjdHkiOiJKV1QiLCJlbmMiOiJBMjU2R0NNIiwiYWxnIjoiUlNBLU9BRVAifQ.ohaQh1fV1Yple6ZnfAeh84_5MToKMDZqo-hnPeAqE9tepmjBy6dh0DKm7BdBnEGaVU-yJv3nJIVH7V7Ng1mQ8Psbj6N3KaFzyM7yTK0RYE0IblFMdsJgHrBw-bTpJMtZJxQt0NNI3lghdLxUdq6K44e7sykYp3UdYoMZK1XLnSaSLMPiVfOY8QZMW6uhGW8YtqrtfD29nhB6EWYmLDMXes3PJj8HyrMxMvlP1DN5ff4vNzJZJ0NDB59SDi_77Itjtrw-vFU-PnFeyXYQVbx0vJyaD7GMK-6Whv6-jy-8wUXJG42K9RD9kW1L_Zm9BMpdRSP6fosclok9ql-ovXqvMg.zApOIl7VrZYeUPT4.Oo-5U-8_jIFNB_Fx9PVmVO-g5Ts9Dlqo56ackW--widAcRxJmjl8J_DwitYftHMs9qfTUAulPcNF2vwo5YUX72Sj-aoux2wmWekSGDTPaElVnQpsLxSAuDgANTxEjcQfmUbVT5EOPCxJ5BEcffXPIjC1EYHBGPiQhjS_svZrN9a-upSLO-X36X_3Bm1CeU2awMBkhYgfHLoUad4tzveMTZloGwRFn5QNwmpe0wqKFmBTf6Pfq7xk0fC4JQfXND8eL1CGqyXZ0cTYQLli7_U4sFogy7Gm9axyIrHAIOaLxzJMWfS5Br1NqcyEaw8_Jvhg5VaRpknzE55UA-MfFU7wCed-96ZWhANNtLslWsOAYveBvcc-p7Df4BdlGREb5InU6v5KS3Zv_nbW5hG5pEKU35qKjEow_F6a25pCrCATcl5UVYt98_fveC0fgF8qvLERbzJObMg1rPnljK2zb5U13Ef-QZ15EghCq0-TK2iGXVJsP-GO7wWEvYiA8oFRxrOF_hdd78o_MmvuDEW_XBXdHw-LIqtzGtUU68jYB3PADOUG0jtqp-XlBEDwSRWrrO_20qt61wv7IUSaqxjU3slArJS7WMW3vTI-m516CLuCfIJfrh_Sf8RuJ4CYTxeUwRuXOOg-HOnpRksIZDGttUwja83OIzBvtmw7MKNv7rpXx8bP0QGwapi-KHKy9Fx1Rp8osLYbvzh3GtWk_FQE0_GjMe8H7aVKEojK8JgxzjoDZFdHzOZcYLFVN48GP1NGi_ZOUakSWCoFg2PlFX8nQIt85VkMTC2E94MOUaqSFT2FfSFQyCa2_BZPIwK4GWmG_9IFk4Ao0XjJjmHbha31mZ4U3nlEycPkV0f6AnCuPklrEnhxef60gluZcfOhlWbi-PZFhS5ZF9wfPi4w__gOFAkKrQD8hBS6xLzEYqvx780qHe68TCTmUMFSs_OdTDpdI5NO7MDzN8m9JWAyqbne95MQY6nIrk-8b6SAqOfi6GYjgHdWGbGHyBvujeNSK5VhrXi4BDJktn7GctmQVYXdlXrtbQAhBnEqO-SXbKna4X77W5MhtTIZYFL0kn1sVGgW5rmGOQ1g6_n9kFsyOtsxiKtd43B3RAo-1QYyO_szujeO3NscMFkCDdByGEBIl4--Gjog1Ujho52SPKnecMKc_9sOdVhdpnN59uJoxykRnhljYt7tGTWcVr5oPNUhh9G4npmbod6oBp5udw4ZVJDw_ppdnbSFUmltaI7FXKbDg1zHGYs0oNSWc54.pZhyHiOQPahD2SBHazlBCQ"}')
#End Fix Login

api = API()

@signals.on(signals.BEFORE_DISPATCH)
def before_dispatch():
    api.new_session()
    plugin.logged_in = api.logged_in

@plugin.route('')
def home(**kwargs):
    folder = plugin.Folder(cacheToDisc=False)

    if not api.logged_in:
        folder.add_item(label=_(_.LOGIN, _bold=True), path=plugin.url_for(login), bookmark=False)
    else:
        folder.add_item(label=_(_.LIVE_TV, _bold=True), path=plugin.url_for(editorial, id=LINEAR_ID, title=_.LIVE_TV))
        _home(folder)

        if settings.getBool('bookmarks', True):
            folder.add_item(label=_(_.BOOKMARKS, _bold=True), path=plugin.url_for(plugin.ROUTE_BOOKMARKS), bookmark=False)

        folder.add_item(label=_.LOGOUT, path=plugin.url_for(logout), _kiosk=False, bookmark=False)

    folder.add_item(label=_.SETTINGS, path=plugin.url_for(plugin.ROUTE_SETTINGS), _kiosk=False, bookmark=False)

    return folder

def _home(folder):
    for row in api.navigation():
        if row['id'] == 'teams':
            continue

        if row['id'] == 'home':
            row['title'] = _.FEATURED

        folder.add_item(
            label = _(row['title'], _bold=True),
            path = plugin.url_for(page, id=row['path'], title=row['title']),
        )

@plugin.route()
def page(id, title, **kwargs):
    folder = plugin.Folder(title)

    for row in api.page(id):
        folder.add_item(
            label = row['title'],
            path = plugin.url_for(editorial, id=row['id'], title=row['title']),
        )

    return folder

def _html_to_text(html):
    soup = BeautifulSoup(html, 'html.parser')

    # Remove <a> tags containing "join now"
    for a_tag in soup.find_all('a'):
        if '>>' in a_tag.get_text().lower():
            a_tag.extract()
    text = '\n\n'.join(soup.stripped_strings)
    return text

@plugin.route()
def article(asset, **kwargs):
    asset = api.asset(asset)

    description = ''
    for row in sorted(asset['contents'], key=lambda x: x['position']):
        if row['type'] == 'RICHTEXT':
            description += row['value']
    gui.text(_html_to_text(description), heading=asset['title'])

@plugin.route()
def editorial(id, title, **kwargs):
    folder = plugin.Folder(title)
    now = arrow.utcnow()

    live_play_type = settings.getEnum('live_play_type', PLAY_FROM_TYPES, default=PLAY_FROM_ASK)

    for row in api.editorial(id):
        is_live = row.get('isLive', False)
        is_linear = row.get('type') == 'linear-channel'

        path = plugin.url_for(play, asset=row['id'], _is_live=is_live)
        if row['type'] == 'article':
            path = plugin.url_for(article, asset=row['id'])

        item = plugin.Item(
            label = row['title'],
            info = {
                'plot': row.get('description'),
                'duration': row.get('duration', 0),
            },
            art = {'thumb': row.get('imageUrl') or DEFAULT_IMG},
            path = path,
            playable = row['type'] != 'article',
            is_folder = False,
        )

        start_time = arrow.get(row['broadcastStartTime']) if 'broadcastStartTime' in row else None

        if start_time and start_time > now:
            item.label += start_time.to('local').format(_.DATE_FORMAT)

        elif is_linear:
            item.path = plugin.url_for(play, asset=row['id'], _is_live=is_live)

        elif is_live:
            item.label = _(_.LIVE, label=item.label)

            item.context.append((_.PLAY_FROM_LIVE, "PlayMedia({})".format(
                plugin.url_for(play, asset=row['id'], play_type=PLAY_FROM_LIVE, _is_live=is_live)
            )))

            item.context.append((_.PLAY_FROM_START, "PlayMedia({})".format(
            plugin.url_for(play, asset=row['id'], play_type=PLAY_FROM_START, _is_live=is_live)
            )))

            item.path = plugin.url_for(play, asset=row['id'], play_type=live_play_type, _is_live=is_live)

        folder.add_items(item)

    return folder

@plugin.route()
def login(**kwargs):
    options = [
        [_.DEVICE_CODE, _device_code],
        [_.EMAIL_PASSWORD, _email_password],
    ]

    index = 0 if len(options) == 1 else gui.context_menu([x[0] for x in options])
    if index == -1 or not options[index][1]():
        return

    gui.refresh()

def _email_password():
    username = gui.input(_.ASK_USERNAME, default=userdata.get('username', '')).strip()
    if not username:
        return

    userdata.set('username', username)

    password = gui.input(_.ASK_PASSWORD, hide_input=True).strip()
    if not password:
        return

    api.login(username=username, password=password)

    return True

def _device_code():
    start = time.time()
    data = api.device_code()
    monitor = xbmc.Monitor()

    with gui.progress(_(_.DEVICE_LINK_STEPS, url=data['verificationUri'], code=data['userCode']), heading=_.DEVICE_CODE) as progress:
        while (time.time() - start) < data['expiresIn']:
            for i in range(data['interval']):
                if progress.iscanceled() or monitor.waitForAbort(1):
                    return

                progress.update(int(((time.time() - start) / data['expiresIn']) * 100))

            if api.device_login(data['deviceCode']):
                return True

@plugin.route()
def logout(**kwargs):
    if not gui.yes_no(_.LOGOUT_YES_NO):
        return

    api.logout()
    gui.refresh()


@plugin.route()
@plugin.plugin_middleware()
def mpd_request(url, _data, _path, **kwargs):
    _data = _data.decode('utf8')

    ## OS1 HACK
    if '/OptusSport1/' in url:
        to_add = r'''\1\n
        <Representation id="1" width="1920" height="1080" frameRate="50/1" bandwidth="8000000" codecs="avc1.640020"/>
        <Representation id="2" width="1280" height="720" frameRate="50/1" bandwidth="5780830" codecs="avc1.640020"/>
        '''
        if settings.getBool('h265', True):
            to_add += '<Representation id="10" width="1920" height="1080" frameRate="50/1" bandwidth="7135999" codecs="hvc1.1.6.H120.B0"/>'
        _data = re.sub('(<Representation .*? width="1280".*?>)', to_add, _data, 1)

    ## OS2 HACK
    elif '/OptusSport2/' in url:
        to_add = r'''\1\n
        <Representation id="2" width="1920" height="1080" frameRate="50/1" bandwidth="8000000" codecs="avc1.640020"/>
        <Representation id="3" width="1280" height="720" frameRate="50/1" bandwidth="5780830" codecs="avc1.640020"/>
        '''
        if settings.getBool('h265', True):
            to_add += '<Representation id="1" width="1920" height="1080" frameRate="50/1" bandwidth="7135999" codecs="hvc1.1.6.H120.B0"/>'
        _data = re.sub('(<Representation .*? width="1280".*?>)', to_add, _data, 1)

    ## OS11 Premier League HACK
    elif '/OptusSport11/' in url:
        to_add = r'''\1\n
        <Representation id="8" width="1920" height="1080" frameRate="50/1" bandwidth="8000000" codecs="avc1.640020"/>
        <Representation id="1" width="1280" height="720" frameRate="50/1" bandwidth="5780830" codecs="avc1.640020"/>
        '''
        if settings.getBool('h265', True):
           to_add += '<Representation id="7" width="1920" height="1080" frameRate="50/1" bandwidth="7135999" codecs="hvc1.1.6.H120.B0"/>'
        _data = re.sub('(<Representation .*? width="1280".*?>)', to_add, _data, 1)

    ## OS12 Laliga HACK
    elif '/OptusSport12/' in url:
        to_add = r'''\1\n
        <Representation id="10" width="1920" height="1080" frameRate="50/1" bandwidth="8000000" codecs="avc1.640020"/>
        <Representation id="1" width="1280" height="720" frameRate="50/1" bandwidth="5780830" codecs="avc1.640020"/>
        '''
        if settings.getBool('h265', True):
           to_add += '<Representation id="11" width="1920" height="1080" frameRate="50/1" bandwidth="7135999" codecs="hvc1.1.6.H120.B0"/>'
        _data = re.sub('(<Representation .*? width="1280".*?>)', to_add, _data, 1)

    with open(_path, 'wb') as f:
        f.write(_data.encode('utf8'))

@plugin.route()
@plugin.login_required()
def play(asset, play_type=PLAY_FROM_LIVE, **kwargs):
    play_type = int(play_type)

    from_start = False
    if play_type == PLAY_FROM_START or (play_type == PLAY_FROM_ASK and not gui.yes_no(_.PLAY_FROM, yeslabel=_.PLAY_FROM_LIVE, nolabel=_.PLAY_FROM_START)):
        from_start = True

    use_cmaf = False #settings.getBool('use_cmaf') and inputstream.require_version('20.3.1')
    stream = api.play(asset, True, use_cmaf=use_cmaf)
    stream['url'] = stream['url'].strip()

    item = plugin.Item(
        path = stream['url'],
        inputstream = inputstream.Widevine(
            license_key=stream['license']['@uri'],
        ),
        headers = HEADERS,
    )

    if stream['protocol'] == 'CMAF':
        item.inputstream.manifest_type = 'hls'
        item.inputstream.mimetype = 'application/vnd.apple.mpegurl'
    elif 'v6/OptusSport' in stream['url'] or 'v7/OptusSport' in stream['url']:
        item.proxy_data['middleware'] = {stream['url']: {'type': MIDDLEWARE_PLUGIN, 'url': plugin.url_for(mpd_request, url=stream['url'])}}

    drm_data = stream['license'].get('drmData')
    if drm_data:
        item.headers['x-axdrm-message'] = drm_data

    if from_start:
        item.resume_from = 1

    return item

@plugin.route()
@plugin.merge()
def playlist(output, **kwargs):
    with codecs.open(output, 'w', encoding='utf8') as f:
        f.write(u'#EXTM3U x-tvg-url="{}"'.format(EPG_URL))

        for row in api.editorial(LINEAR_ID):
            if row.get('type') != 'linear-channel':
                continue

            f.write(u'\n#EXTINF:-1 tvg-id="{id}" tvg-logo="{logo}",{name}\n{url}'.format(
                id=row['channel']['id'], logo=row.get('imageUrl') or DEFAULT_IMG, name=row['title'], url=plugin.url_for(play, asset=row['id'], _is_live=True)))

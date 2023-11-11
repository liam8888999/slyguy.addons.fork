from collections import defaultdict

from kodi_six import xbmc
from six.moves.urllib_parse import unquote

from slyguy import plugin, settings, inputstream
from slyguy.log import log
from slyguy.util import get_system_arch


from .language import _
from .yt_dlp import YoutubeDL


@plugin.route('/')
def home(**kwargs):
    if kwargs.get('action') == 'play_video':
        return plugin.redirect(plugin.url_for(play, video_id=kwargs.get('videoid')))

    folder = plugin.Folder()
    folder.add_item(label='TEST 4K', playable=True, path=plugin.url_for(play, video_id='NECyQhw4-_c'))
    folder.add_item(label='TEST 4K HDR', playable=True, path=plugin.url_for(play, video_id='tO01J-M3g0U'))
    folder.add_item(label=_.SETTINGS, path=plugin.url_for(plugin.ROUTE_SETTINGS), _kiosk=False, bookmark=False)
    return folder

def play_android_apk(yturl):
    start_activity = 'StartAndroidActivity(,android.intent.action.VIEW,,"{}")'.format(yturl)
    log.debug(start_activity)
    xbmc.executebuiltin(start_activity)

@plugin.route('/play')
def play(video_id, **kwargs):
    yturl = "https://www.youtube.com/watch?v={}".format(video_id)
    log.debug("YouTube URL {}".format(yturl))

    is_android = get_system_arch()[0] == 'Android'

    if is_android and settings.getBool('play_with_youtube_apk', False):
        return play_android_apk(yturl)

    ydl_opts = {
        'quiet': True,
        'cachedir': None,
        'no_warnings': True,
    }

    try:
        with YoutubeDL(ydl_opts) as ydl:
            data = ydl.extract_info(yturl, download=False)
    except Exception as e:
        log.exception(e)
        data = {}

    groups = defaultdict(list)
    for x in data.get('formats', []):
        if 'container' not in x:
            continue

        if x['container'] == 'webm_dash':
            if x['vcodec'] != 'none':
                groups['video/webm'].append(x)
            else:
                groups['audio/webm'].append(x)
        elif x['container'] == 'mp4_dash':
            groups['video/mp4'].append(x)
        elif x['container'] == 'm4a_dash':
            groups['audio/mp4'].append(x)

    if not groups:
        if is_android and settings.getBool('fallback_youtube_apk', False):
            return play_android_apk(yturl)

        raise plugin.PluginError('No videos found')

    headers = {}
    str = '<MPD minBufferTime="PT1.5S" mediaPresentationDuration="PT{}S" type="static" profiles="urn:mpeg:dash:profile:isoff-main:2011"><Period>'.format(data["duration"])
    for idx, (group, formats) in enumerate(groups.items()):
        str += '<AdaptationSet id="{}" mimeType="{}"><Role schemeIdUri="urn:mpeg:DASH:role:2011" value="main"/>'.format(idx, group)
        for format in formats:
            headers.update(format['http_headers'])
            format['url'] = unquote(format['url']).replace("&", "&amp;").replace('"', "&quot;").replace("<", "&lt;").replace(">", "&gt;")
            codec = format['vcodec'] if format['vcodec'] != 'none' else format['acodec']
            str += '<Representation id="{}" codecs="{}" bandwidth="{}"'.format(format["format_id"], codec, format["bitrate"])
            if format['vcodec'] != 'none':
                str += ' width="{}" height="{}" frameRate="{}/1001"'.format(format["width"], format["height"], format["fps"]*1000)
            str += '>'
            if format['acodec'] != 'none':
                str += '<AudioChannelConfiguration schemeIdUri="urn:mpeg:dash:23003:3:audio_channel_configuration:2011" value="2"/>'
            str += '<BaseURL>{}</BaseURL><SegmentBase indexRange="{}-{}"><Initialization range="{}-{}" /></SegmentBase>'.format(
                format["url"], format["indexRange"]["start"], format["indexRange"]["end"], format["initRange"]["start"], format["initRange"]["end"]
            )
            str += '</Representation>'
    
        str += '</AdaptationSet>'
    str += '</Period></MPD>'

    path = 'special://temp/test.mpd'
    with open(xbmc.translatePath(path), 'w') as f:
        f.write(str)

    #TODO Subtitles
    return plugin.Item(
        path = path,
        inputstream = inputstream.MPD(),
        headers = headers,
    )

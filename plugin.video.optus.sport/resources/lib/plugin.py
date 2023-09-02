import codecs
import re
import time

import xbmc
import xbmcaddon
import xbmcgui
import xbmcplugin

import arrow
from kodi_six import xbmc

from slyguy import plugin, gui, settings, userdata, signals, inputstream
from slyguy.constants import PLAY_FROM_TYPES, PLAY_FROM_ASK, PLAY_FROM_LIVE, PLAY_FROM_START, MIDDLEWARE_PLUGIN

from .api import API
from .language import _
from .constants import *

#Fix LOGIN
#run string through https://www.freeformatter.com/xml-escape.html#ad-output and press unescape before pasting here
a = xbmcaddon.Addon()
a.setSettingString('_userdata', '{"username":"ssmith@pafc.com.au","user_id":"d1b7bd50-5f54-4999-81a5-042a72906cbf","id_token":"eyJraWQiOiJtVXVkT2o2S2s0TVZHU3pGSEZTbTd4TmlwaEVvUHhFMlVBK2NBWlJyOXRjPSIsImFsZyI6IlJTMjU2In0.eyJzdWIiOiJkMWI3YmQ1MC01ZjU0LTQ5OTktODFhNS0wNDJhNzI5MDZjYmYiLCJjdXN0b206cHBpZCI6IjM0MTJlZWJkLWEzZDQtNGU3Yi05Y2RiLTk2Zjk1Zjg2YjlmMCIsImlzcyI6Imh0dHBzOlwvXC9jb2duaXRvLWlkcC5hcC1zb3V0aGVhc3QtMi5hbWF6b25hd3MuY29tXC9hcC1zb3V0aGVhc3QtMl91RHJlbG5uaGsiLCJjb2duaXRvOnVzZXJuYW1lIjoiZDFiN2JkNTAtNWY1NC00OTk5LTgxYTUtMDQyYTcyOTA2Y2JmIiwiY3VzdG9tOnZlbmRvclRva2VuIjoiQmVhcmVyIGJjNWFlZWI4LTcxNmYtNDQ1MC1iNzQzLWJmN2IyMmY3MjBiMiIsImN1c3RvbTp2ZW5kb3JUb2tlblRpbWUiOiIxNTc3MzQ0NDM2MzU5IiwiY3VzdG9tOnVzZXJJZCI6IjIxMzI2MzkiLCJjdXN0b206dXNlclR5cGUiOiJwcmVtaXVtIiwiYXVkIjoiNGY5ajQ1azMwMjQxNDNsOGhjazFrMW8ydHAiLCJldmVudF9pZCI6IjUwZjFiOGEzLTllN2UtNGM2NC04MjdlLTBjNDE4M2FiNjA4MyIsInRva2VuX3VzZSI6ImlkIiwiYXV0aF90aW1lIjoxNjkxNDk1MzcxLCJuYW1lIjoiU2hhbmUgU21pdGgiLCJwaG9uZV9udW1iZXIiOiIrNjE0MDk0MDUyNDIiLCJleHAiOjE2OTM2MjU2MzgsImlhdCI6MTY5MzYxNDgzOCwiZW1haWwiOiJzc21pdGhAcGFmYy5jb20uYXUifQ.cWzWUHnelimCHIbDVyEm6bH0URSKFBKPKdx5CdtJwaNRyaUoOS0X-ztImo8yPElR4Bo48th7TMOALlH_jEG8ORglCuCQyENNUJFhJhx50HXbOm9W20Vn4TOXyaTAIgvaU_vkWdKPzlIhLizxK9JPb_i1kD5VXn7P_M-R5JwOFXhIK_g0-9PWWzmUqjT0TB7AMw1vWlYz5hZePuTtJFrFNtZeRXWONBACrqc1g1KQAzUJLa8sfsRVFiJDHk_SIhNoWDI9oWV6UjM5bC8Kan7L8FAFMQhtuiEvGAAJELcSlTyNrRHrlvgsp925sdhJZpyGt5D-N5VyIGQzgxV9V5bsQQ","expires":1693625623,"refresh_token":"eyJjdHkiOiJKV1QiLCJlbmMiOiJBMjU2R0NNIiwiYWxnIjoiUlNBLU9BRVAifQ.rnG69RhL7Gp2FBrqXJvmnSFAQE-JHCt5bsYBv3Qh6_Lm2RxuHLIRjy5SuVrdwQoRwB0UYgZPmKZn8th9H1rsGp9NqFL2N8S5g74CgT9IjhvyXknxuKl0wS3JpoqPpd44xDSPBhBJYrTdfPYPkY20rZ74Sy5M2JMNmzJy0hPUWnszaI2G-e-Ho09ZnZsV1IwbBIQWG2vgS_2lMdfIaTz7l5ea6V1-tvIM3e4NmWqwwEASt6yd7eOjNmkAaxQ3S4Vr3lI8C3mYprbxvlD8foCwDDzfGu0s2mUeLUq4GfyBgG6YXP4WBvloZN9Clv-6Jv7-I0H7HBoc8XSe4RVAPXyZJw.qIdFV31-atlnLUbp.akxvwgjwkLAH5r5SQ0L3RJ5XrKWD7Hq8ry2gvEW_hJbMFnPUbSc6zqXbbYs2v5fIAbw-CHjxr5tg0n5I6ufpNRh9cNVcYd9SmB08nInxPhlCmSFkvYLEHSBUjzS9Me-NoD_zegX-Ssu56JFgzA7Urk1weLuCPnrGPRb3C8xbJ_g407y_px35GABEFFApBOS6AOZSFBgAOa0XpsJC3sboj8KPH7Ug99Gwdwz15FMSlOOOtrmJYV5RlcbPvHAPoP2-rElWP5o4CoC4M6fPk3iimIh4oOJU3KzCKeqT8_ry45UkXk1w0Zl75H8-8porTnt_zcX1q6zNwgKMMNpniEtOh7XNd6mlIaFBmHvDh7plNha4iJlxtf6WjXDbvyabS7etSijEqAi7ruW76cxN_D7zalv3_4kpsRP34W7OCpqDc_Tg8Eh-trM-kikYf8EzrSRdSWmMjnY5613a39r6cNE_m36ECa2unnU8vhfFYjL8otXQdcdDYPgwl-8xvrIdKepNdxZgU53JgDH-rmXvoIMFBZzYXF5RtbQ9LTsNzPXb2K2fG5qGp2hLYeD5gEqiK_MnvzN2xrfzHPP8Y9veUHfY5O_oTZ36WnfKquRvDdiamOZYP6bv1rc89880GBytzB73hbkl7l-nREBvLuvV23xeVR0X_WN5T2HX1jNKpGtz4Ck50gdUIcPjH8fHRZXZJQpSghyzivYFaGRTDOiAJ3kCkTpPNbCz10fbpuW5nOH53dt9-DvHzGP8ZfwzuTgoL6bZyYgTrO2Wac7K5NzjNSgM0ytc-uHTS114mH-opxtNMnOCUG5D5Oq9iMpKRoK0Kx8zGGROdp7ZqPk50hzXOd4khKrcIsRM1XcJdmEKDghi_wrta1ecMyKPLwsBik2RZOtsTel7_ZkLYxUxiK5bxpChQGxQj-HDkMhOQCCB38gbMuax1co-U79yvFZnC-PA288jhwPLdO85bi1cJse1sBlAG6fALqS2qMHmhqr3VQzZmnBv5SROqXunPGqAIG9PfME3hGFS0NPE2qZD_O4V2QTu6egWV998a2B9T_hoQoeqKxrDG21tZVWg1yvhf7ebhRlJ2SzhXKfRWkVZb8vxbdBuTLLAtsGz9QUpeimGNILxw2wYMPdrhBocCGujE1EIixPpSuztygpC-if_d_T0HoGJ1NoXzh5_KLW1xbOiKUfBR_Hmt5IhcGYfXGUC7fUTUqHxmIrHdJEMRiyYOeGOXZk0Ij5bBcB-kBwSFrydbBYcT3NLPdhqXYR499lPXrj-8YG43r_s3mrZS3GRLEbQh2Nx9M2xz5AytoaNnLTIj9sJCIkZW_D0Ti9zAPleP9r_mtYPN5eHSMU-Bxf1.jPnaIryh_8Gt5VTutbhwKg"}')
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

@plugin.route()
def editorial(id, title, **kwargs):
    folder = plugin.Folder(title)
    now = arrow.utcnow()

    live_play_type = settings.getEnum('live_play_type', PLAY_FROM_TYPES, default=PLAY_FROM_ASK)

    for row in api.editorial(id):
        is_live = row.get('isLive', False)
        is_linear = row.get('type') == 'linear-channel'

        item = plugin.Item(
            label = row['title'],
            info  = {
                'plot': row.get('description'),
                'duration': row.get('duration', 0),
            },
            art   = {'thumb': row.get('imageUrl') or DEFAULT_IMG},
            path  = plugin.url_for(play, asset=row['id'], _is_live=is_live),
            playable = True,
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

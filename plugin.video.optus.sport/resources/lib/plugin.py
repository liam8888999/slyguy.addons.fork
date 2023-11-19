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
a.setSettingString('_userdata', '{"username":"jimmy_w83@yahoo.com","user_id":"612946f9-e1fc-4094-bf08-42092b6d6637","id_token":"eyJraWQiOiJtVXVkT2o2S2s0TVZHU3pGSEZTbTd4TmlwaEVvUHhFMlVBK2NBWlJyOXRjPSIsImFsZyI6IlJTMjU2In0.eyJzdWIiOiI2MTI5NDZmOS1lMWZjLTQwOTQtYmYwOC00MjA5MmI2ZDY2MzciLCJjdXN0b206cHBpZCI6IjM4N2RiMzRhLTBkNTUtNDE0NS04MTlkLWI5ZDA1OGVkNjlhOCIsImlzcyI6Imh0dHBzOlwvXC9jb2duaXRvLWlkcC5hcC1zb3V0aGVhc3QtMi5hbWF6b25hd3MuY29tXC9hcC1zb3V0aGVhc3QtMl91RHJlbG5uaGsiLCJjb2duaXRvOnVzZXJuYW1lIjoiNjEyOTQ2ZjktZTFmYy00MDk0LWJmMDgtNDIwOTJiNmQ2NjM3IiwiY3VzdG9tOnZlbmRvclRva2VuIjoiQmVhcmVyIGQxZDExMmJlLTI0MjItNGYwYS1iNjQ4LWYyZGU0OWQ3NWM0NiIsImN1c3RvbTp2ZW5kb3JUb2tlblRpbWUiOiIxNTUxOTg5MTk0NTk4IiwiY3VzdG9tOnVzZXJJZCI6IjM4MDc1NiIsImN1c3RvbTp1c2VyVHlwZSI6InByZW1pdW0iLCJhdWQiOiI0ZjlqNDVrMzAyNDE0M2w4aGNrMWsxbzJ0cCIsImV2ZW50X2lkIjoiNTAyYTFkMTktYzU0OS00YmM3LWJmYjgtZDE0NzYzNTdhZjM0IiwidG9rZW5fdXNlIjoiaWQiLCJhdXRoX3RpbWUiOjE2OTk5NDQxNDUsIm5hbWUiOiJqaW1teV93ODNAeWFob28uY29tIiwiZXhwIjoxNjk5OTU0OTQ1LCJpYXQiOjE2OTk5NDQxNDUsImVtYWlsIjoiamltbXlfdzgzQHlhaG9vLmNvbSJ9.CJ_FrQzkeAclYEJnOsoNzmW-mWL_fvRQa_cjCt-N2TMDNfDmwEU1GIcMiGSuk9ua-pR0viYyeYw8m858xuKUmp1sWW83F-h5L2vvYONCNfUKLoLvpPfBGrWGPuGj6EZ3d2Z_E6LOaurWsIPqiAmjSH7BmFT5lcMD4fZhohg5nR9LIB3zWMietNFAZXq46HqL5PCVEHUNqq-bKv2pyvbHWaG_5V3eh4-C7M-bEgi056edDVjmyLc55xd9ISb9CnjWGQe_6Hm_Z1tZHlKESN6sfE9J4zLULHtHRWPszYTz4Afv8SBz6S0DW9ForVmPKR8m9N3Lo69-QTG_TZ-i_fWXWw","expires":1699954931,"refresh_token":"eyJjdHkiOiJKV1QiLCJlbmMiOiJBMjU2R0NNIiwiYWxnIjoiUlNBLU9BRVAifQ.Ni-FYCzuaeMkd1pxZi7mYmOz92NyCIipTMPKLZRoEhe3dQuvLjA4_A6yA_aPybZVMxPfioubTeL0BSF0tfYTlNAbAteX7xYQZoflXVj81hAOQQO2zA1U9mCcCbzgD5c9mqnMaFVZVClz-5CtSKF_QT4hdf_aAEOA3CaIBZRQB8N-ZvtXOE4POkVn7ZUeRA4u_ugCBLavmvNY-2H3cfxmkZXXGZb02H3neP6mQU_NsHmEVyyUSSgkKEfvWk6DU3dCRIdwZH16psX5kz8-69OzMnPURbw8LPdfAwt2OscZpAKQlmabWTDjjRulS8qeaHtxop_jm9L4dnyTcikY6kJr2g.CjFOf4BuI3e6ZGhS.YaO1aQSuU6G_Om79O2lmBNU2Y9rOvNQi3j9O7qRKbzQ3yN_7t98TSKyh3wZayRcDO271WBZO7ABFhGe0GLD51Y__MPKyr3cxuvtZb1TOljBBMUSnqup9G2SE73rNT8UfKcfLxbzICo8Qu7Oplg_xRb2NmCGfutF2tynO3i3bfpsfLVYZe-BEKbgd5T_stVHElNrALqZckjRZqkB6MQRFKKwtydAWsyhCMZwAs6E00y-186kd7SFNz-cTcr7xNru7lzn3z4kmZAWMlka4kFBAU5lRukQpTtnHLvTWG4QI0NfFNSzRzass1a04O7QAfQTmDRkSKblhKbgLNEyQ7w3eW3hCXJTKmtWgONKg3LFB7OQ21uFX26w5dSd2p1k-isNJzz4qmKzWngbLxrMbWILjAw8QBiwW33prEFx7JNPx8KfImBtljM4SSHc5RsgPiEvDwXtjzIOsC85B37w6NFfZ08uIXPpGVzUJYWNdLdD0O1KP-q2Gcwad5K3Y1GVynviqs1NBH3c7fjIDt0hMy12z_RNb-t66gPMPfwrOa5lzkc_-hmFAG5bhDwkYlZYW1kvOaA3AYzCb_7EDDGnuqq9G8fJFTk2kxr4iSEK6W2F_H4_eA_zpC3M7RK813ubzlgWkAQovsvRqdjSR9KKWfRWLJ_KJ6NIQ4YcKT0KKtawq-45yDzu3kHJwfhM2UOLUdUhRuy8WuU6xUV3YgiddKCFLLi5ef1VNPsNzzk8KbWb51nsj0EWFER5tDGuIit-g9VZeCKAO9ZVlxACJ5q1Y3kLL06j6gVW9ET_TBZxDSFOLF-RphQBDWQRkhGqGWi12WDFtd739jCGPShFirQAnaBWUCIYSgbGFieKQfPJl8PiIGdd6QXqDyRao0gQxITSt6CHeKDEknqbwq4SkrCFEDtpLHzT2htA0CKXw0DdQhpSQ5MWZ6Buaodpgh6juZiYeBWQ-fHQyWdG7nx2zKWwC2jHBaVMtZQU_f7Tdq6q8L6Czm0lArFJenqPvuJ6WvUsBi0KN8tBWmJ9c5gFnnTHlMbrN5YnC211WPgdLJd4TrPo2v1yeaWj7UyJpC-DEOYTWKx6uNgCo6NSQ8w-wfqdkjaRLFUmQx8K-tdU85DEKHh8wICZDMvdKP8j-HE_GM9VSmvmNsppsJMHE34V2unkuoZuH77z2gbBxrdCPbN1vG4FThPjOWahZSItv8yVUx3aSlEYezaNgFmth1QW8JD7f_faJwn6yLNbPXE5wmz0XgEw2BpoPDsS4ncFDm230dTHO1Hy58O_-xCI2UfJVns3K6yP1L-l-WqEYyFvzYpxVGjZ3a4rj5uHZduCxVicdjtvAdwin7rwD5dL7a5Hb.FlJ46wIkkzDnSF27o8B2uQ"}')
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

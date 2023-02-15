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
a.setSettingString('_userdata', '{"username":"stamedes1@optusnet.com.au","user_id":"914fc847-9394-409b-9aa5-4b4c3f48b114","id_token":"eyJraWQiOiJtVXVkT2o2S2s0TVZHU3pGSEZTbTd4TmlwaEVvUHhFMlVBK2NBWlJyOXRjPSIsImFsZyI6IlJTMjU2In0.eyJzdWIiOiI5MTRmYzg0Ny05Mzk0LTQwOWItOWFhNS00YjRjM2Y0OGIxMTQiLCJpc3MiOiJodHRwczpcL1wvY29nbml0by1pZHAuYXAtc291dGhlYXN0LTIuYW1hem9uYXdzLmNvbVwvYXAtc291dGhlYXN0LTJfdURyZWxubmhrIiwiY29nbml0bzp1c2VybmFtZSI6IjkxNGZjODQ3LTkzOTQtNDA5Yi05YWE1LTRiNGMzZjQ4YjExNCIsImN1c3RvbTp2ZW5kb3JUb2tlbiI6IkJlYXJlciA3NTA1NzZmZC02MTU1LTQ2N2ItYTAwZi0yMGRmY2E3YTVlNTAiLCJjdXN0b206dmVuZG9yVG9rZW5UaW1lIjoiMTU1NDU2MDg5NzcxOCIsImN1c3RvbTp1c2VySWQiOiIxNzU4NzYiLCJjdXN0b206dXNlclR5cGUiOiJwcmVtaXVtIiwiYXVkIjoiNGY5ajQ1azMwMjQxNDNsOGhjazFrMW8ydHAiLCJldmVudF9pZCI6Ijk4YmEyNTFlLTU2ZWMtNGVkOS1hOTdjLWVkOTViZDUzMDRiZSIsInRva2VuX3VzZSI6ImlkIiwiYXV0aF90aW1lIjoxNjIxOTEyMTQ0LCJuYW1lIjoic3RhbWVkZXMxQG9wdHVzbmV0LmNvbS5hdSIsImV4cCI6MTY0NTUzOTMzMiwiaWF0IjoxNjQ1NTI4NTMyLCJlbWFpbCI6InN0YW1lZGVzMUBvcHR1c25ldC5jb20uYXUifQ.R-NtP8hxtuS23S-a5YZXockSht2FUI2UG8thyAwJyZbR6S2z05IGrMonHWdG2tjMwRMA-6iLi7ief8SY7BXkhkevF5PGvBUGGcPssMto1YeLlsiXIzyyrrEYo947U7CiYajY9qC9PzWa5m-N1hyuSvYl9UDw8rcYSZvhUWX0SzgSpFHMaAE7yzvgnZZ4vSmRAmTyrKesEASr1E-2qLMYACC5T81kHecXHqGRzrc8UJ5YsNtEwIAqF4ngjUsSd_-MPd07N3s9BB5t9fM4VdSJCIncdlma4V_CZoOp5cq5TZ8q6Z9OGTVUyftol1X5_-5HAPXSc1POYeQl4XtxoBksYw","expires":1645539317,"refresh_token":"eyJjdHkiOiJKV1QiLCJlbmMiOiJBMjU2R0NNIiwiYWxnIjoiUlNBLU9BRVAifQ.sQhHeMCd-1zCG9q23L-fXo7RwkqvH1-6wAhU4zGOE6m7NLzm6XaLcirWFXZ0WudA8VAbU51IqroMw70f1IJxY77_16OWmh2hqqJPmo0DO0l_Tox0YREDEXFWDqJGGo0yAj3hWyd5F66S-Fosq-KKMXzPspA5em7TUeY5qPm7YajKk8QEpssqFvTMm72k7i2SYaXWApd4NLve_GRg23nGJZd4fsOHJdqt2511enyPB96z9Y6S1AWfa4o7G1iOO_Q9uahhqlKNM0CTLNGKiyufheO211R4QWJ73JSRaef__zhaqP9RdSsX2PheCKFZSwqrVDbcCGm-wjsT_8eqHf1lvQ.pmKcoVx_KC5JK5A4.VCzBRcMMw2pGZtI9q5ZFkhBTTnSnba1F87IXX2gGjjvHuElrqtraQme9DQ8SoKvsfiDq3JKf0ZRd0NRJmcs4BY3Tyt2eawYQpqND0ZNzN7JKPzVnvaU3i7tLGQJp09Icx-GbRhyRIyzYqlPyjQdIxF9XYct3Z3Bye1v9_NI7lr7_mARKU4XgMp8LBX5u867t-nJfIWPLB4XLeOeTGk7de7bedZ-9zMXHHU3OeJqJ9-FEdsACMyBOIDEhs-B1bKaoDVOXUDcmIgxqXifSzmO5gip_XzChIEX8PkHTNiD2AF23H0TQHPFTad-pWW2c8GShzlYhG7cMsk_na-lbSGicLM0EjYB0tccUrTkibCqM-EWMuFL_FRdS2bAGiC3yu7ptTzHMCEW8jAPtquqD6f6uVcFnXvLdU43D5V_cwsGJ6-ZsusQKh0aPH5F_VUQ7aVfsh1ZCiEtlc35xuqIYzwMFPV_og2Ne1X6sxw669RRMNdysFsKXCKwjDfdvzLAtvYN2_kZwN4r9CAHX_YnUxc3cVnIq0hFNNbjmzV9N1tXge_nRdPN9k63xKukIk9oLoZZDcxfCUqEh4_5-KIIcSco1enS4oRQvDw74GUozvzfDTb3yAvyaSd5bRwxvAHKgf6QeTlxWU6Jj8J0CycRSuqxdNlxB6TtSv3ECki8-b_jtzEaq0r7zkEaY958Ng8uR4o10jsJIvdVALjn02IcsDILyM5eti30JDTByGXdYvlWGRy3i3hx8ywcSarJf-HpR0YybofR00-Fh7UmEMrkwMn2gBrim9zdKzCuJq1jn5TMLrQUkP8tcQop_Nkr5tKgGXAS5i1Dw-O6Ze75tC53hROhsPnm45gn0vewqTrz1o6LddXgDeaGX5KfFFhiVX49JY2VBGksJ8ssXnHjZ7IDPhA3OQw_sc2HuKI2MgBE3EuOgtv81YxNDZ0eHthNmeJnhKINTTXGPS1PYbu4D_lPliqBxhAU8-uBUUHnD_ZHlvExVAVeDaaULuuWw0V41TPGBMjtBdo8RC-y7AuVKsCD49Q835O0Xe73d_IfvPdF_w99HQeMIcgPNtyMjmMn7dn47bIiud4tE4jYLH5xWS1SiIzi9-BQ_XbHeVikOgqi_-4NZZNhIVUhY-wBjD62Hra6x6DOGlvWPHhTlOT_XjBt7tfGQOxj3s4ydwcQPDFEU4wARrQho_ZrIVXbrURsDKWBf782cCETRUPxjFWYEJchoYYAQqmXG_OYMmUu8WWY6jYl_aP4kTw1hRE4bEXPt2cN2gi5m33a4_EewjZar4zzfIxWLRiFlDR1Rtb3GbUSvfQwhbjTY9FZaHWPaeYGkJ3Ktp_UDwEfo31H2yN6V.DgeYUQgTqVvtCJfvyZDJtA"}')
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
        _data = re.sub('(<Representation id="11" width="1280".*?>)', to_add, _data, 1)

    ## OS2 HACK
    elif '/OptusSport2/' in url:
        to_add = r'''\1\n
        <Representation id="7" width="1280" height="720" frameRate="50/1" bandwidth="5780830" codecs="avc1.640020"/>
        '''
        if settings.getBool('h265', True):
            to_add += '<Representation id="8" width="1920" height="1080" frameRate="50/1" bandwidth="7135999" codecs="hvc1.1.6.H120.B0"/>'
        _data = re.sub('(<Representation id="13" width="1280".*?>)', to_add, _data, 1)

    ## OS11 Premier League HACK
    elif '/OptusSport11/' in url:
        to_add = r'''\1\n
        <Representation id="8" width="1920" height="1080" frameRate="50/1" bandwidth="8000000" codecs="avc1.640020"/>
        <Representation id="1" width="1280" height="720" frameRate="50/1" bandwidth="5780830" codecs="avc1.640020"/>
        '''
        if settings.getBool('h265', True):
           to_add += '<Representation id="7" width="1920" height="1080" frameRate="50/1" bandwidth="7135999" codecs="hvc1.1.6.H120.B0"/>'
        _data = re.sub('(<Representation id="11" width="1280".*?>)', to_add, _data, 1)

    ## OS12 Laliga HACK
    elif '/OptusSport12/' in url:
        to_add = r'''\1\n
        <Representation id="10" width="1920" height="1080" frameRate="50/1" bandwidth="8000000" codecs="avc1.640020"/>
        <Representation id="1" width="1280" height="720" frameRate="50/1" bandwidth="5780830" codecs="avc1.640020"/>
        '''
        if settings.getBool('h265', True):
           to_add += '<Representation id="11" width="1920" height="1080" frameRate="50/1" bandwidth="7135999" codecs="hvc1.1.6.H120.B0"/>'
        _data = re.sub('(<Representation id="12" width="1280".*?>)', to_add, _data, 1)

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

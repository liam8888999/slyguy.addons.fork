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

from slyguy import plugin, gui, userdata, signals, inputstream
from slyguy.constants import PLAY_FROM_TYPES, PLAY_FROM_ASK, PLAY_FROM_LIVE, PLAY_FROM_START, MIDDLEWARE_PLUGIN

from .api import API
from .language import _
from .constants import *
from .settings import settings


#Fix LOGIN
#run string through https://www.freeformatter.com/xml-escape.html#ad-output and press unescape before pasting here
a = xbmcaddon.Addon()
a.setSettingString('_userdata', '{"username":"PizzutoAE_95@hotmail.com","user_id":"b2a94c77-1210-4dcb-8a07-3aae0b3c3ccd","id_token":"eyJraWQiOiJtVXVkT2o2S2s0TVZHU3pGSEZTbTd4TmlwaEVvUHhFMlVBK2NBWlJyOXRjPSIsImFsZyI6IlJTMjU2In0.eyJzdWIiOiJiMmE5NGM3Ny0xMjEwLTRkY2ItOGEwNy0zYWFlMGIzYzNjY2QiLCJjdXN0b206cHBpZCI6ImM0YzEwOTRlLTg0MTQtNDUxYy1iYWRlLTg2ZWFhMjEzNWY3ZCIsImlzcyI6Imh0dHBzOlwvXC9jb2duaXRvLWlkcC5hcC1zb3V0aGVhc3QtMi5hbWF6b25hd3MuY29tXC9hcC1zb3V0aGVhc3QtMl91RHJlbG5uaGsiLCJjb2duaXRvOnVzZXJuYW1lIjoiYjJhOTRjNzctMTIxMC00ZGNiLThhMDctM2FhZTBiM2MzY2NkIiwiY3VzdG9tOnZlbmRvclRva2VuIjoiQmVhcmVyIGE3ZTk2NTM1LTZjZWYtNDFkYy1hMDNiLTk4MDEwZGQxMGUyNiIsImN1c3RvbTp2ZW5kb3JUb2tlblRpbWUiOiIxNTY4NzE2MTUzMzU5IiwiY3VzdG9tOnVzZXJJZCI6Ijk0OTc4NSIsImN1c3RvbTp1c2VyVHlwZSI6InByZW1pdW0iLCJhdWQiOiI0ZjlqNDVrMzAyNDE0M2w4aGNrMWsxbzJ0cCIsImV2ZW50X2lkIjoiMWYzOGE4NDUtYzFlYi00ZWM4LThiMDQtMTZjYmZkYmI0NjRhIiwidG9rZW5fdXNlIjoiaWQiLCJhdXRoX3RpbWUiOjE3MjA1ODY0MzEsIm5hbWUiOiJBbmRyZXcgUGl6enV0byBDcm9rZSIsInBob25lX251bWJlciI6Iis2MTQzMTYxODg3OCIsImV4cCI6MTcyMDU5NzIzMSwiaWF0IjoxNzIwNTg2NDMxLCJlbWFpbCI6InBpenp1dG9hZV85NUBob3RtYWlsLmNvbSJ9.DpwIdVrGSWlQKIRBymO8jV_XHZSIY68FAR0yI9BFm3z2d1LBudfdOoVHWdyU7_x7-mo9zgWIjpxqXis0OA5auYhGmpyO5WpDgUo6Gkmmh5hk9XGFD8PR5poOe6CWP8iWxx7Mqv0r4ryd_s_EGYZ8nf1rAyVL6UQo0vC_6tlgOab3k6vo_fKW92N3KVAyjk6139Eo9s_SflSGbXief2QqZKgrief2XglUY5n6oP9bnyVj-d-wjFROHC9AphbOW6pK3Uw58Vp5dQrFh3hsftgxQKnAhySnmdyjB3HrIDkVCMVkTfYXXCmSc119hcyDGoD6EPjHbRSgwByuqT1xe4FEVQ","expires":1720597216,"refresh_token":"eyJjdHkiOiJKV1QiLCJlbmMiOiJBMjU2R0NNIiwiYWxnIjoiUlNBLU9BRVAifQ.t9gG5OzcDYcovLu5tONpxqDN99ceF7SFTn63pbeDuF5pUrrhlvgL0d5cXjKE2ytoYDeqeLFnhddbnWwX26pguzxrnx2Jlea4ktDLOda9b1x2HaZe1G1Hn0GE4axWQWQpCBWTKK8nJxBQy2NLdiYn-wjOfDnP8VffoG-FSXqyr_17YoCM9ln-0DjHap82T7yCf1d-27C8Rll6zeUx3ItAxUNGrpjSV-Obyhe5wsWGzl8FAiuS7nOvgSsMl1s_XOXhnvU22AEdC5If2E1Knd2SiFzNv_T-z95hyy_GAjHufdkWu1pHUedx_88T6_v_KuxibItp4wmfD4lksAbhFaTE4Q.Fy76-UKMDt8xJCGt.XZxFakVb88j3Bzbh3OmfCUir9VkBq73nJUnpFnGKpwNp33sqLLwXs1jrIPV9v7IvflmtLHUldNK9nnxVEXlDTN4s4VxftBsPy603Q4vamSGGixi66k0hckoPRQ0sDwPH6h73L7TohyzzUEHsEX3dUjmQEChGAyKq2CPzeyYg6GLZbvZyMiwViKnI-703KpzlUSCNz_fpb6dOeVrkW0BQKerh6qPDBzeMGbxHpL_zbb_W3uLJIKdwkmElXibu-Gs2ItWAuFI114D7keKbORg1HPCPe99JjA02lc8dsILlcZL80tYXCulBG9yo2jPNaAD1E-DqVClrMsOAFRdwef4FO_3EhDQ44VU1rkc3gCuCewwxeu53lw6gEHZO15gz_w21XtJ3UEULRLQrLhSPmL_e1FOZu_D8sjEG7heT3tvdtaVERnKNahof6UoKyMl1X-dcw6NSH7IHeQmg6eehcv05LCjb79Tv3QI3wQ80zpvGm9ZFoFY9vLEB1oVN6meXJMfcpp0Wiz1i4_-jcFShZ95PJ07-6TLaaY8eS1vhBIvUnXL4-07BzKgQe8TLHwYXajhghCSGeLZfT9dtwmB5JBUXM0bMwVtwh-AASQn8xsSgcdvL48xEOsLU8U3B4WLCDQT-Y5cHZcFfTB5vRx7oMffAp9or6M9ByTQ65n-4wsdzR_JY6MyREVk_sk9xfN3PDUTZst_Wn1Uw4vhItZio9rbSHNPxJ46FlvIiQWN4WO1CRrIYs6G-bL9hrMu6Nx1OmajpWzg2MY5Uhy8vA2Unu-PFyYHF4Vwl821bVT9JwdvE8lozjtZy9XZtgJZY7Xsi5BDvEmqEgT2ca7-eZjFOaxChVN0aS0bPgGWgW-BF9563Dd4xworlQb0vrr90SCGxFOSYiqftutn-M46e1PiVQd_YcqxmbTLyp61cvhsW3Aiv_Lbw4TFPRcS7xtSHF3tMQqLpyQ3QVtfRoS7fv-VjVaZKGc42p7acEQyZK5N1397YMgsZ-PRagebuW58-ZKNEkuBWqQkONmch_PseDrRuRhB7a5EsslV48-c6RNE9FGCShSX2twyaT3KaXwNW0N9zZmrQWCv-WH0ZCsgW7o8mFZ7daJOEC0ivoHSoDyKfQnYJKB-A2q2gsqYLx9WTG1UoiqHIAepMeKUk-rgbeiYhihEUR1ONcJiOKge_Mi2ResOzd8TlSgn7n5THaIxmCN2elgQNg2YSMTxodQ4O4r5OG9jcm57GCtCU3tO4nwULLRzjRQVu2zx7I1FiUeoQt4y3on_5jHFMuIlN8QvEVZU5v3_IRiGXhwEmWd9NNpTMax4drB9Kyzvn_107pvPgJG-q8-qruLxkTZnph4YJ.TKKG_9ul4I6ZFAoBXGBcdg"}')
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
            item.path = plugin.url_for(play, asset=row['id'], linear=1, _is_live=is_live)

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
    username = gui.input(_.ASK_EMAIL, default=userdata.get('username', '')).strip()
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

    ## OS1 / OS2 / Premiere / Laliga
    if '/OSG1/' in url or '/OSG2/' in url or '/OSG11/' in url or '/OSG12/' in url:
        to_add = r'''\1\n
        <Representation id="_1080p50avc" width="1920" height="1080" frameRate="50/1" bandwidth="8000000" codecs="avc1.640020"/>
        <Representation id="_1080p50hevc" width="1920" height="1080" frameRate="50/1" bandwidth="7135999" codecs="hvc1.1.6.H120.B0"/>
        '''
        _data = re.sub('(<Representation .*? width="1280".*?>)', to_add, _data, 1)

    with open(_path, 'wb') as f:
        f.write(_data.encode('utf8'))

@plugin.route()
@plugin.login_required()
def play(asset, play_type=PLAY_FROM_LIVE, linear=0, **kwargs):
    play_type = int(play_type)
    linear = int(linear)

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
    elif linear:
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
                id=row['channel']['id'], logo=row.get('imageUrl') or DEFAULT_IMG, name=row['title'], url=plugin.url_for(play, asset=row['id'], linear=1, _is_live=True)))

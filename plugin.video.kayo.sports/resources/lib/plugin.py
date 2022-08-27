import codecs
import time

import xbmc
import xbmcaddon
import xbmcgui
import xbmcplugin

import arrow
from kodi_six import xbmc

from slyguy import plugin, gui, settings, userdata, signals, inputstream
from slyguy.log import log
from slyguy.exceptions import PluginError
from slyguy.constants import PLAY_FROM_TYPES, PLAY_FROM_ASK, PLAY_FROM_LIVE, PLAY_FROM_START, ROUTE_RESUME_TAG, ROUTE_LIVE_TAG

from .api import API
from .language import _
from .constants import *

#Fix LOGIN
#run string through https://www.freeformatter.com/xml-escape.html#ad-output and press unescape before pasting here
a = xbmcaddon.Addon()
a.setSettingString('_userdata', '{"username":"a301uuv@gmail.com","access_token":"eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCIsImtpZCI6Ik56aEJPVFJHT0RjNE1FUkRSRFJEUTBVd1FrVkdNRGt4TVVVNVF6RTRRa0UzTkVVMk1rVkRRZyJ9.eyJodHRwOi8vZm94c3BvcnRzLmNvbS5hdS9tYXJ0aWFuX2lkIjoiYXV0aDB8NWQ0MTlmMDNhY2IxMzgwYzhiNzA1N2I3IiwiaHR0cHM6Ly92aW1vbmQvZW50aXRsZW1lbnRzIjpbeyJzdm9kIjoiNTcwIiwicXVhbGl0eSI6ImFsbCIsInN0cmVhbWNvdW50IjoyfV0sImh0dHBzOi8va2F5b3Nwb3J0cy5jb20uYXUvc3RhdHVzIjp7ImFjY291bnRfc3RhdHVzIjoiQUNUSVZFX1NVQlNDUklQVElPTiIsInN1Yl9hY2NvdW50X3N0YXR1cyI6IlBBWUlOR19TVUJTQ1JJUFRJT04iLCJwcHZfZXZlbnRzIjpbXSwidXBkYXRlZF9hdCI6IjIwMjItMDItMjJUMDk6MTM6MjkuNzE1WiJ9LCJodHRwczovL2FyZXMuY29tLmF1L3N0YXR1cyI6eyJhY2NvdW50X3N0YXR1cyI6IlZFUklGSUVEX0lERU5USVRZIiwic3ViX2FjY291bnRfc3RhdHVzIjoiVkVSSUZJRURfTU9CSUxFIiwicHB2X2V2ZW50cyI6W10sInVwZGF0ZWRfYXQiOiIyMDIyLTAyLTIyVDA5OjEzOjI5LjcxNVoifSwiaHR0cDovL2lyZGV0by5jb20vY29udHJvbC9lbnQiOlt7ImVwaWQiOiJBbmRyb2lkVFZfS0FZT18ySEQiLCJiaWQiOiJCQVNJQyJ9XSwiaHR0cDovL2lyZGV0by5jb20vY29udHJvbC9qdGkiOiI2ZWYxMWI3ZS02YWYyLTRlMzgtYWNjOC03ZDU5N2M4ZjZiZmMiLCJodHRwOi8vaXJkZXRvLmNvbS9jb250cm9sL2FpZCI6InN0cmVhbW90aW9uIiwiaXNzIjoiaHR0cHM6Ly9hdXRoLnN0cmVhbW90aW9uLmNvbS5hdS8iLCJzdWIiOiJhdXRoMHw1ZDQxOWYwM2FjYjEzODBjOGI3MDU3YjciLCJhdWQiOlsic3RyZWFtb3Rpb24uY29tLmF1IiwiaHR0cHM6Ly9wcm9kLW1hcnRpYW4uYXUuYXV0aDAuY29tL3VzZXJpbmZvIl0sImlhdCI6MTY0NTUyNzAxMywiZXhwIjoxNjQ1NTM3ODEzLCJhenAiOiJhMG4xNHhhcDdqcmVFWFBmTG85RjZKTHBScDNYZWgybCIsInNjb3BlIjoib3BlbmlkIG9mZmxpbmVfYWNjZXNzIGRybTpoaWdoIGVtYWlsIHVzZXI6cGhvbmVfdmVyaWZpZWQifQ.oIHo-akCWPMAK-Je9ugxHq2dKXgoIWJgF54cem7YvcjIISWDgawfNNDrIXb6gFzYYl_HSIx-02_LtOSYg3GgbGtPcJWRkGpWQ9MoStzkQVwr9MoBCJtNg2WpI8shXyIUFKfNtYwsE_Rb9Ds6h_wWYaIVTubgWiIhHB7-iJU6d24moaALLgfeaISnEPes58WkZq0YEtydZhvmdMCkCiTgQh3enLmn9MOHY8F5SYJ7P7yjlLrkEr15E6g2CkUk5ViTFhqZ--yCEEaFz_E7Ut7n7bb-FwK_lcJISxA_mtGKSn5YXchE_tCKZf09fKJyKXkDpf0jdRZbd6kKdV9xD3YnKw","expires":1645537798,"refresh_token":"v_333qkqBnka4x8KSj-3upCA8B3KETPze_qQwiVrhOL-P","avatar":"https://resources.kayosports.com.au/production/avatars/2.png","profile_name":"Adam","profile_id":"01f8fa12adbb08d66f2a8f0d6ba9a1ebe4618c3d"}')
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
        folder.add_item(label=_(_.FEATURED, _bold=True), path=plugin.url_for(featured))
        folder.add_item(label=_(_.SHOWS, _bold=True), path=plugin.url_for(shows))
        folder.add_item(label=_(_.SPORTS, _bold=True), path=plugin.url_for(sports))
        folder.add_item(label=_(_.LIVE_CHANNELS, _bold=True), path=plugin.url_for(live))
        folder.add_item(label=_(_.SEARCH, _bold=True), path=plugin.url_for(search))

        if settings.getBool('bookmarks', True):
            folder.add_item(label=_(_.BOOKMARKS, _bold=True), path=plugin.url_for(plugin.ROUTE_BOOKMARKS), bookmark=False)

        folder.add_item(label=_.SELECT_PROFILE, path=plugin.url_for(select_profile), art={'thumb': userdata.get('avatar')}, info={'plot': userdata.get('profile_name')}, _kiosk=False, bookmark=False)
        folder.add_item(label=_.LOGOUT, path=plugin.url_for(logout), _kiosk=False, bookmark=False)

    folder.add_item(label=_.SETTINGS, path=plugin.url_for(plugin.ROUTE_SETTINGS), _kiosk=False, bookmark=False)

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

    _select_profile()
    gui.refresh()

def _device_code():
    start = time.time()
    data = api.device_code()
    monitor = xbmc.Monitor()

    with gui.progress(_(_.DEVICE_LINK_STEPS, url=data['verification_uri'], code=data['user_code']), heading=_.DEVICE_CODE) as progress:
        while (time.time() - start) < data['expires_in']:
            for i in range(data['interval']):
                if progress.iscanceled() or monitor.waitForAbort(1):
                    return

                progress.update(int(((time.time() - start) / data['expires_in']) * 100))

            if api.device_login(data['device_code']):
                return True

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

def _live_channels():
    panel_id = None
    for row in api.landing('sports'):
        if row['title'].lower() == 'live channels':
            panel_id = row['id']
            break

    if not panel_id:
        raise PluginError(_.LIVE_PANEL_ID_MISSING)

    channels = []
    data = api.panel(panel_id)
    live_data = api.channel_data()

    for row in data.get('contents', []):
        if row['contentType'] != 'video':
            continue

        row['data']['chno'] = None
        row['data']['epg'] = []
        if row['data']['asset']['id'] in live_data:
            row['data']['chno'] = live_data[row['data']['asset']['id']]['chno']
            row['data']['epg'] = live_data[row['data']['asset']['id']]['epg']

        channels.append(row['data'])

    return sorted(channels, key=lambda x: (x is None, x['chno'] or 9999))

@plugin.route()
def live(**kwargs):
    folder = plugin.Folder(_.LIVE_CHANNELS)
    show_chnos = settings.getBool('show_chnos', True)

    if settings.getBool('show_epg', True):
        now = arrow.now()
        epg_count = 5
    else:
        epg_count = None

    for channel in _live_channels():
        item = _parse_video(channel)
        if not item:
            continue

        if channel['chno'] and show_chnos:
            item.label = _(_.LIVE_CHNO, chno=channel['chno'], label=item.label)

        plot = u''
        if epg_count:
            count = 0
            for index, row in enumerate(channel.get('epg', [])):
                start = arrow.get(row[0])
                try: stop = arrow.get(channel['epg'][index+1][0])
                except: stop = start.shift(hours=1)

                if (now > start and now < stop) or start > now:
                    plot += u'[{}] {}\n'.format(start.to('local').format('h:mma'), row[1])
                    count += 1
                    if count == epg_count:
                        break

        if plot:
            item.info['plot'] = plot

        folder.add_items(item)

    return folder

@plugin.route()
@plugin.login_required()
def logout(**kwargs):
    if not gui.yes_no(_.LOGOUT_YES_NO):
        return

    api.logout()
    userdata.delete('avatar')
    userdata.delete('profile_name')
    userdata.delete('profile_id')
    gui.refresh()

@plugin.route()
def featured(**kwargs):
    folder = plugin.Folder(_.FEATURED)
    folder.add_items(_landing('home' if api.is_subscribed() else 'free'))
    return folder

@plugin.route()
def shows(**kwargs):
    folder = plugin.Folder(_.SHOWS)
    folder.add_items(_landing('shows'))
    return folder

@plugin.route()
@plugin.search()
def search(query, page, **kwargs):
    data = api.search(query=query, page=page)
    return _parse_contents(data.get('results', [])), data['pages'] > page

@plugin.route()
def sports(**kwargs):
    folder = plugin.Folder(_.SPORTS)

    for row in api.sport_menu():
        slug = row['url'].split('sport!')[1]

        folder.add_item(
            label = row['name'],
            path  = plugin.url_for(sport, slug=slug, title=row['name']),
            art   = {
                'thumb': SPORT_LOGO.format(row['sport']),
            },
        )

    folder.add_items(_landing('sports'))

    return folder

@plugin.route()
def sport(slug, title, **kwargs):
    folder = plugin.Folder(title)
    folder.add_items(_landing('sport', sport=slug))
    return folder

@plugin.route()
def season(show_id, season_id, title, **kwargs):
    data = api.show(show_id=show_id, season_id=season_id)
    folder = plugin.Folder(title)

    for row in data:
        if row['title'] == 'Episodes':
            folder.add_items(_parse_contents(row.get('contents', [])))

    return folder

@plugin.route()
def show(show_id, title, **kwargs):
    data = api.show(show_id=show_id)

    folder = plugin.Folder(title)

    for row in data:
        if row['title'] == 'Seasons':
            for row2 in row.get('contents', []):
                asset = row2['data']['asset']

                folder.add_item(
                    label = asset['title'],
                    art  = {
                        'thumb': _get_image(asset, 'show', 'thumb'),
                        'fanart': _get_image(asset, 'show', 'fanart'),
                    },
                    info = {
                        'plot': asset.get('description-short'),
                    },
                    path = plugin.url_for(season, show_id=show_id, season_id=asset['id'], title=asset['title']),
                )

    return folder

@plugin.route()
def panel(id, sport=None, **kwargs):
    data = api.panel(id, sport=sport)
    folder = plugin.Folder(data['title'])
    folder.add_items(_parse_contents(data.get('contents', [])))
    return folder

@plugin.route()
@plugin.login_required()
def select_profile(**kwargs):
    _select_profile()
    gui.refresh()

def _select_profile():
    profiles = api.profiles()

    options = []
    values  = []
    default = -1

    avatars = {}
    for avatar in api.profile_avatars():
        avatars[avatar['id']] = avatar['url']

    for index, profile in enumerate(profiles):
        profile['avatar'] = avatars.get(profile['avatar_id'])

        values.append(profile)
        options.append(plugin.Item(label=profile['name'], art={'thumb': profile['avatar']}))

        if profile['id'] == userdata.get('profile_id'):
            default = index
            _set_profile(profile, notify=False)

    index = gui.select(_.SELECT_PROFILE, options=options, preselect=default, useDetails=True)
    if index < 0:
        return

    _set_profile(values[index])

def _set_profile(profile, notify=True):
    userdata.set('avatar', profile['avatar'])
    userdata.set('profile_name', profile['name'])
    userdata.set('profile_id', profile['id'])

    if notify:
        gui.notification(_.PROFILE_ACTIVATED, heading=profile['name'], icon=profile['avatar'])

def _landing(name, sport=None):
    items = []

    for row in api.landing(name, sport=sport):
        if row['title'].lower() == 'live channels':
            continue

        if row['panelType'] == 'hero-carousel' and row.get('contents') and settings.getBool('show_hero_contents', True):
            items.extend(_parse_contents(row['contents']))

        elif row['panelType'] != 'hero-carousel' and 'id' in row:
            items.append(plugin.Item(
                label = row['title'],
                path  = plugin.url_for(panel, id=row['id'], sport=sport),
            ))

    return items

def _parse_contents(rows):
    items = []

    for row in rows:
        if row['contentType'] == 'video':
            items.append(_parse_video(row['data']))

        elif row['contentType'] == 'section':
            items.append(_parse_section(row['data']))

    return items

def _parse_section(row):
    # If not asset, we are probably linking directly to a sport or something..
    if 'asset' not in row or row.get('type') == 'search-icon':
        return

    asset = row['asset']

    return plugin.Item(
        label = asset['title'],
        art = {
            'thumb': _get_image(asset, 'show', 'thumb'),
            'fanart': _get_image(asset, 'show', 'fanart'),
        },
        info = {
            'plot': asset.get('description-short'),
        },
        path = plugin.url_for(show, show_id=asset['id'], title=asset['title']),
    )

def _get_image(asset, media_type, img_type='thumb', width=None):
    if not asset.get('image-pack'):
        images = asset.get('images') or {}
        image_url = images.get('defaultUrl')
        if not image_url:
            return None
    else:
        image_url = IMG_URL.format(asset['image-pack'])

    image_url += '?location={}&imwidth={}'

    if img_type == 'thumb':
        return image_url.format('carousel-item', width or 415)

    elif img_type == 'fanart':
        return image_url.format('hero-default', width or 1920)

def _makeTime(start=None):
    return start.to('local').format('h:mmA') if start else ''

def _makeDate(now, start=None):
    if not start:
        return ''

    if now.year == start.year:
        return start.to('local').format('DD MMM')
    else:
        return start.to('local').format('DD MMM YY')

def _makeHumanised(now, start=None):
    if not start:
        return ''

    now = now.to('local').replace(hour = 0, minute = 0, second = 0, microsecond = 0)
    start = start.to('local').replace(hour = 0, minute = 0, second = 0, microsecond = 0)
    days = (start - now).days

    if days == -1:
        return 'yesterday'
    elif days == 0:
        return 'today'
    elif days == 1:
        return 'tomorrow'
    elif days <= 7 and days >= 1:
        return start.format('dddd')
    else:
        return _makeDate(now, start)

def _parse_video(row):
    asset = row['asset']
    display = row['contentDisplay']

    now = arrow.now()
    start = arrow.get(asset['transmissionTime'])
    precheck = start

    if 'preCheckTime' in asset:
        precheck = arrow.get(asset['preCheckTime'])
        if precheck > start:
            precheck = start

    title = display.get('heroTitle') or display['title'] or asset['title']
    if 'heroHeader' in display:
        title += ' [' + display['heroHeader'].replace('${DATE_HUMANISED}', _makeHumanised(now, start).upper()).replace('${TIME}', _makeTime(start)) + ']'

    if not api.is_subscribed():
        is_free = asset.get('isFreemium', False)

        if settings.getBool('hide_locked', False) and not is_free:
            return None
        elif not is_free:
            title = _(_.LOCKED, label=title)

    item = plugin.Item(
        label = title,
        art  = {
            'thumb' : _get_image(asset, 'video', 'thumb'),
            'fanart': _get_image(asset, 'video', 'fanart'),
        },
        info = {
            'plot': display.get('description'),
            'plotoutline': display.get('description'),
            'mediatype': 'video',
        },
        playable = True,
        is_folder = False,
    )

    is_live = False
    play_type = settings.getEnum('live_play_type', PLAY_FROM_TYPES, default=PLAY_FROM_ASK)

    start_from = ((start - precheck).seconds)
    if start_from < 1:
        start_from = 1

    if now < start:
        is_live = True

    elif asset['assetType'] == 'live-linear':
        is_live = True
        start_from = 0
        play_type = PLAY_FROM_LIVE

    elif asset['isLive'] and asset.get('isStreaming', False):
        is_live = True

        item.context.append((_.PLAY_FROM_LIVE, "PlayMedia({})".format(
            plugin.url_for(play, id=asset['id'], play_type=PLAY_FROM_LIVE, _is_live=is_live)
        )))

        item.context.append((_.PLAY_FROM_START, "PlayMedia({})".format(
            plugin.url_for(play, id=asset['id'], start_from=start_from, play_type=PLAY_FROM_START, _is_live=is_live)
        )))

    item.path = plugin.url_for(play, id=asset['id'], start_from=start_from, play_type=play_type, _is_live=is_live)

    return item

@plugin.route()
@plugin.login_required()
def play(id, start_from=0, play_type=PLAY_FROM_LIVE, **kwargs):
    start_from = int(start_from)
    play_type = int(play_type)
    is_live = ROUTE_LIVE_TAG in kwargs

    if is_live:
        if play_type == PLAY_FROM_LIVE:
            start_from = 0
        elif play_type == PLAY_FROM_ASK:
            start_from = plugin.live_or_start(start_from)
            if start_from == -1:
                return

    asset = api.stream(id)
    streams = [asset['recommendedStream']]
    streams.extend(asset['alternativeStreams'])
    streams = [s for s in streams if s['mediaFormat'] in SUPPORTED_FORMATS]
    if not streams:
        raise PluginError(_.NO_STREAM)

    prefer_cdn = settings.getEnum('prefer_cdn', AVAILABLE_CDNS)
    prefer_format = SUPPORTED_FORMATS[0]

    if prefer_cdn == CDN_AUTO:
        try:
            data = api.use_cdn(is_live, sport=asset['metadata'].get('sport'))
            prefer_cdn = data['useCDN']
            prefer_format = 'ssai-{}'.format(data['mediaFormat']) if data['ssai'] else data['mediaFormat']
            if prefer_format.startswith('ssai-'):
                log.debug('Stream Format: Ignoring prefer ssai format')
                prefer_format = prefer_format[5:]
        except Exception as e:
            log.debug('Failed to get preferred cdn')
            prefer_cdn = AVAILABLE_CDNS[0]

    providers = [prefer_cdn]
    providers.extend([s['provider'] for s in streams])

    formats = [prefer_format]
    formats.extend(SUPPORTED_FORMATS)

    streams = sorted(streams, key=lambda k: (providers.index(k['provider']), formats.index(k['mediaFormat'])))
    stream = streams[0]

    log.debug('Stream CDN: {provider} | Stream Format: {mediaFormat}'.format(**stream))

    item = plugin.Item(
        path = stream['manifest']['uri'],
        headers = HEADERS,
    )

    item.headers.update({'authorization': 'Bearer {}'.format(userdata.get('access_token'))})

    ## Cloudfront streams start from correct position
    if stream['provider'] == CDN_CLOUDFRONT and start_from:
        start_from = 1

    if stream['mediaFormat'] == FORMAT_DASH:
        item.inputstream = inputstream.MPD()

    elif stream['mediaFormat'] in (FORMAT_HLS_TS, FORMAT_HLS_TS_SSAI):
        force = stream['mediaFormat'] == FORMAT_HLS_TS_SSAI or (is_live and play_type == PLAY_FROM_LIVE and asset['assetType'] != 'live-linear')
        item.inputstream = inputstream.HLS(force=force, live=is_live)
        if force and not item.inputstream.check():
            raise PluginError(_.HLS_REQUIRED)

    elif stream['mediaFormat'] in (FORMAT_HLS_FMP4, FORMAT_HLS_FMP4_SSAI):
        ## No audio on ffmpeg or IA
        item.inputstream = inputstream.HLS(force=True, live=is_live)
        if not item.inputstream.check():
            raise PluginError(_.HLS_REQUIRED)

    elif stream['mediaFormat'] in (FORMAT_DRM_DASH, FORMAT_DRM_DASH_HEVC):
        item.inputstream = inputstream.Widevine(
            license_key = LICENSE_URL,
        )

    if start_from and not ROUTE_RESUME_TAG in kwargs:
        item.resume_from = start_from

    return item

@plugin.route()
@plugin.merge()
def playlist(output, **kwargs):
    with codecs.open(output, 'w', encoding='utf8') as f:
        f.write(u'#EXTM3U x-tvg-url="{}"'.format(EPG_URL))

        for row in _live_channels():
            asset = row['asset']

            f.write(u'\n#EXTINF:-1 tvg-id="{id}" tvg-chno="{channel}" channel-id="{channel}" tvg-logo="{logo}",{name}\n{url}'.format(
                id=asset['id'], channel=row['chno'] or '', logo=_get_image(asset, 'video', 'thumb'),
                    name=asset['title'], url=plugin.url_for(play, id=asset['id'], _is_live=True)))

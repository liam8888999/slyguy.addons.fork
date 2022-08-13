import codecs
import time
import re

import arrow
from slyguy import plugin, gui, settings, userdata, signals, inputstream
from slyguy.log import log
from slyguy.monitor import monitor
from slyguy.exceptions import PluginError
from slyguy.constants import ROUTE_LIVE_TAG, PLAY_FROM_TYPES, PLAY_FROM_ASK, PLAY_FROM_LIVE, PLAY_FROM_START, LIVE_HEAD, ROUTE_RESUME_TAG

from .api import API
from .language import _
from .constants import *

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
        # folder.add_item(label=_(_.FEATURED, _bold=True), path=plugin.url_for(landing, slug='home', title=_.FEATURED))
        # folder.add_item(label=_(_.CHANNELS, _bold=True), path=plugin.url_for(landing, slug='channels', title=_.CHANNELS))
        # folder.add_item(label=_(_.CATEGORIES, _bold=True), path=plugin.url_for(landing, slug='categories', title=_.CATEGORIES))
        folder.add_item(label=_(_.LIVE_CHANNELS, _bold=True), path=plugin.url_for(live))
        # folder.add_item(label=_(_.SEARCH, _bold=True), path=plugin.url_for(search))

        if settings.getBool('bookmarks', True):
            folder.add_item(label=_(_.BOOKMARKS, _bold=True),  path=plugin.url_for(plugin.ROUTE_BOOKMARKS), bookmark=False)

        folder.add_item(label=_.SELECT_PROFILE, path=plugin.url_for(select_profile), art={'thumb': _get_avatar(userdata.get('avatar_id'))}, info={'plot': userdata.get('profile_name')}, _kiosk=False, bookmark=False)
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

@plugin.route()
def landing(slug, title, **kwargs):
    folder = plugin.Folder(title)
    folder.add_items(_landing(slug))
    return folder

def _landing(slug, params=None):
    items = []
    to_add = []

    def expand(row):
        if not row['personalised'] and row.get('contents'):
            items.extend(_parse_contents(row.get('contents', [])))
        else:
            data = api.panel(link=row['links']['panels'])
            items.extend(_parse_contents(data.get('contents', [])))

    for row in api.landing(slug, params)['panels']:
        if slug=='shows' and 'channels' in row['title'].lower():
            continue

        if row['panelType'] == 'hero-carousel' and settings.getBool('show_hero_contents', True):
            expand(row)

        elif row['panelType'] not in ('hero-carousel', 'genre-menu-sticky') and 'id' in row:
            to_add.append(row)

    if not items and len(to_add) == 1:
        expand(to_add[0])
    else:
        for row in to_add:
            items.append(plugin.Item(
                label = row['title'],
                path  = plugin.url_for(panel, link=row['links']['panels']),
            ))

    return items

def _live_channels():
    data = None
    for row in api.landing('channels')['panels']:
        if 'by news channel' in row['title'].lower():
            data = row
            break

    if not data:
        raise PluginError(_.LIVE_PANEL_ID_MISSING)

    if not data.get('contents', []):
        data = api.panel(panel_id=row['id'])

    channels = []
    live_data = api.channel_data()

    for row in data.get('contents', []):
        channel_id = row['data']['contentDisplay']['linearProvider']
        if not channel_id:
            continue

        row['data']['chno'] = None
        row['data']['epg'] = []
        if channel_id in live_data:
            row['data'].update(live_data[channel_id])
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
        item = plugin.Item(
            label = channel['contentDisplay']['title']['value'],
            playable = True,
            art = {
                'thumb': channel['contentDisplay']['images']['tile'].replace('${WIDTH}', '400'),
            },
            path = plugin.url_for(play_channel, channel_id=channel['contentDisplay']['linearProvider'], _is_live=True),
        )

        if channel['chno'] and show_chnos:
            item.label = _(_.LIVE_CHNO, chno=channel['chno'], label=item.label)

        plot = u''
        count = 0
        if epg_count:
            for index, row in enumerate(channel.get('epg', [])):
                start = arrow.get(row[0])
                try: stop = arrow.get(channel['epg'][index+1][0])
                except: stop = start.shift(hours=1)

                if (now > start and now < stop) or start > now:
                    plot += u'[{}] {}\n'.format(start.to('local').format('h:mma'), row[1])
                    count += 1
                    if count == epg_count:
                        break

        if not count:
            plot += channel.get('description', '')

        item.info['plot'] = plot
        folder.add_items(item)

    return folder

@plugin.route()
def genre(slug, title, genre, subgenre=None, **kwargs):
    folder = plugin.Folder(title)

    params = {'genre': genre}
    if subgenre:
        params['subgenre'] = subgenre

    folder.add_items(_landing(slug, params))
    return folder

@plugin.route()
@plugin.search()
def search(query, page, **kwargs):
    data = api.search(query=query)

    if 'panels' in data:
        items = _parse_contents(data['panels'][0].get('contents', []))
    else:
        items = []

    return items, False

@plugin.route()
def show(show_id, title, **kwargs):
    folder = plugin.Folder(title)
    data = api.landing('show', {'show': show_id})
    seasons = []
    episodes = []
    heros = []
    for row in data['panels']:
        if row['panelType'] == 'tags':
            for row in row.get('contents', []):
                item = plugin.Item(
                    label = row['data']['clickthrough']['title'],
                    art  = {
                        'thumb': data['meta']['socialImage'].replace('${WIDTH}', str(768)),
                        'fanart': row['data']['contentDisplay']['images']['hero'].replace('${WIDTH}', str(1920)),
                    },
                    info = {
                        'plot': row['data']['contentDisplay']['synopsis'],
                        'tvshowtitle': title,
                        'mediatype': 'season',
                    },
                    path = plugin.url_for(season, show_id=show_id, season_id=row['data']['id'], title=title),
                )

                try:
                    season_num = int(re.search('[0-9]+', item.label).group(0))
                except:
                    season_num = 999

                seasons.append([season_num, item])
        elif row['panelType'] == 'synopsis-carousel-tabbed' and row['title'] == 'Episodes':
            episodes.extend(_parse_contents(row.get('contents', [])))
        elif row['panelType'] == 'hero-carousel':
            heros.extend(_parse_contents(row.get('contents', [])))

    if seasons:
        folder.add_items([x[1] for x in sorted(seasons, key=lambda x: x[0])])
    elif episodes:
        folder.add_items(episodes)
    else:
        folder.add_items(heros)

    return folder

@plugin.route()
def season(show_id, season_id, title, **kwargs):
    data = api.landing('show', {'show': show_id, 'season': season_id})
    folder = plugin.Folder(title)
    for row in data['panels']:
        if row['panelType'] == 'synopsis-carousel-tabbed':
            items = _parse_contents(row.get('contents', []))
            for item in items:
                if item.info.get('episode'):
                    folder.add_items(item)

    return folder

@plugin.route()
def panel(panel_id=None, link=None, title=None, **kwargs):
    data = api.panel(panel_id=panel_id, link=link)
    folder = plugin.Folder(title or data['title'])
    folder.add_items(_parse_contents(data.get('contents', [])))
    return folder

def _get_asset(row):
    asset = {
        'id': row['id'],
        'type': row.get('type'),

        'plot': row['contentDisplay']['synopsis'],
        'title': row['contentDisplay']['title']['value'],
        'thumb': row['contentDisplay']['images']['tile'].replace('${WIDTH}', str(768)),
        'fanart': row['contentDisplay']['images']['hero'].replace('${WIDTH}', str(1920)),

        'transmissionTime': row['clickthrough']['transmissionTime'],
        #'preCheckTime': row['clickthrough'].get('preCheckTime'),
        'isStreaming': row['clickthrough']['isStreaming'],
        'asset_id': row['clickthrough']['asset'],
        'newschannel': row['contentDisplay']['linearProvider'].replace('-',' ').upper(),

        'playbackType': None,
    }

    if 'playback' in row:
        asset.update({
            'asset_id': row['playback']['info']['assetId'],
            'playbackType': row['playback']['info']['playbackType'],
            'showtitle': row['playback']['info'].get('show'),
            'duration': row['playback']['info'].get('mediaDuration'),
        })

    for line in row['contentDisplay']['infoLine']:
        if line['type'] == 'episode':
            season  = re.search('S([0-9]+)', line['value'])
            episode = re.search('EP([0-9]+)', line['value'])
            if episode:
                asset['episode'] = int(episode.group(1))
            if season:
                asset['season'] = int(season.group(1))
        elif line['type'] == 'imdb':
            asset['rating'] = line['value']
        elif line['type'] == 'years':
            asset['year'] = int(line['value'])
        # elif line['type'] == 'length' and not asset.get('duration'):
        #     asset['duration'] = 0
        #     match = re.search('([0-9]+)h', line['value'], re.IGNORECASE)
        #     if match:
        #        asset['duration'] += int(match.group(1))*3600
        #     match = re.search('([0-9]+)m', line['value'], re.IGNORECASE)
        #     if match:
        #        asset['duration'] += int(match.group(1))*60
        #     match = re.search('([0-9]+)s', line['value'], re.IGNORECASE)
        #     if match:
        #        asset['duration'] += int(match.group(1))

    return asset

def _parse_contents(rows):
    items = []

    for row in rows:
        asset = _get_asset(row['data'])

        if row['contentType'] == 'video' and asset['asset_id']:
            items.append(_parse_video(asset))

        elif row['contentType'] == 'section' and row['data']['type'] == 'feature-film':
            items.append(_parse_video(asset))

        elif row['contentType'] == 'section' and row['data']['type'] == 'tv-show':
            items.append(_parse_show(asset))

        elif row['contentType'] == 'section' and row['data']['type'] == 'tv-season':
            items.append(plugin.Item(
                label = row['data']['clickthrough']['title'],
                info = {
                    'plot': row['data']['contentDisplay']['synopsis'],
                    'tvshowtitle': row['data']['contentDisplay']['title']['value'],
                    'mediatype': 'season',
                },
                art = {
                    'thumb' : row['data']['contentDisplay']['images']['tile'].replace('${WIDTH}', str(768)),
                    'fanart': row['data']['contentDisplay']['images']['hero'].replace('${WIDTH}', str(1920)),
                },
                path = plugin.url_for(season, show_id=row['data']['clickthrough']['show'], season_id=row['data']['clickthrough']['season'], title=row['data']['contentDisplay']['title']['value']),
            ))

        elif row['contentType'] == 'section' and row['data']['contentType'] == 'genre-menu':
            items.append(plugin.Item(
                label = row['data']['clickthrough']['title'],
                art  = {
                    'thumb' : row['data']['contentDisplay']['images']['menuItemSelected'].replace('${WIDTH}', str(320)),
                },
                path  = plugin.url_for(genre, slug=row['data']['clickthrough']['type'], title=row['data']['clickthrough']['title'], genre=row['data']['clickthrough']['genre'], subgenre=row['data']['clickthrough']['subgenre']),
            ))

        elif row['contentType'] == 'section' and row['data']['contentType'] == 'collection':
            items.append(_parse_collection(asset))

    return items

def _parse_collection(asset):
    return plugin.Item(
        label = asset['title'],
        art  = {
            'thumb': asset['thumb'],
            'fanart': asset['fanart'],
        },
        info = {
            'plot': asset['plot'],
        },
        path = plugin.url_for(collection, collection_id=asset['id'], title=asset['title']),
    )

@plugin.route()
def collection(collection_id, title, **kwargs):
    folder = plugin.Folder(title, no_items_label='Sorry, collections are not yet supported in this add-on')
    return folder

def _parse_show(asset):
    return plugin.Item(
        label = asset['title'],
        art  = {
            'thumb': asset['thumb'],
            'fanart': asset['fanart'],
        },
        info = {
            'plot': asset['plot'],
            'tvshowtitle': asset['title'],
            'mediatype': 'tvshow',
        },
        path = plugin.url_for(show, show_id=asset['id'], title=asset['title']),
    )

def _parse_video(asset):
    now = arrow.now()
    start = arrow.get(asset['transmissionTime'])
    precheck = start

    #if asset['preCheckTime']:
    #    precheck = arrow.get(asset['preCheckTime'])
    #    if precheck > start:
    #        precheck = start

    #log.debug(asset)

    if 'live-tv' in asset['type']:
        asset['plot'] = asset['title']
        asset['title'] = asset['newschannel'] + ' [LIVE]'

    item = plugin.Item(
        label = asset['title'],
        art = {
            'thumb': asset['thumb'],
            'fanart': asset['fanart'],
        },
        info = {
            'plot': asset['plot'],
            #'rating': asset.get('rating'),
            #'season': asset.get('season'),
            #'episode': asset.get('episode'),
            #'tvshowtitle': asset.get('showtitle'),
            #'duration': asset.get('duration'),
            #'year': asset.get('year'),
            #'mediatype': 'episode' if asset.get('showtitle') else 'movie',
        },
        playable = True,
        is_folder = False,
    )

    is_live = False
    play_type = settings.getEnum('live_play_type', PLAY_FROM_TYPES, default=PLAY_FROM_ASK)
    start_from = ((start - precheck).seconds)

    if start_from < 0:
        start_from = 0

    if now < start:
        is_live = True

    elif asset['type'] == 'live-linear':
        is_live = True
        start_from = 0
        play_type = PLAY_FROM_START

    elif asset['playbackType'] == 'LIVE':
        is_live = True

        item.context.append((_.PLAY_FROM_LIVE, "PlayMedia({})".format(
            plugin.url_for(play, id=asset['asset_id'], play_type=PLAY_FROM_LIVE, _is_live=is_live)
        )))

        item.context.append((_.PLAY_FROM_START, "PlayMedia({})".format(
            plugin.url_for(play, id=asset['asset_id'], start_from=start_from, play_type=PLAY_FROM_START, _is_live=is_live)
        )))

    item.path = plugin.url_for(play, id=asset['asset_id'], start_from=start_from, play_type=play_type, _is_live=is_live)

    return item

@plugin.route()
@plugin.login_required()
def logout(**kwargs):
    if not gui.yes_no(_.LOGOUT_YES_NO):
        return

    api.logout()
    userdata.delete('avatar_id')
    userdata.delete('profile_name')
    userdata.delete('profile_id')
    gui.refresh()

@plugin.route()
@plugin.login_required()
def select_profile(**kwargs):
    _select_profile()
    gui.refresh()

def _select_profile():
    options = []
    values  = []
    default = -1
    for index, profile in enumerate(api.profiles()):
        values.append(profile)
        options.append(plugin.Item(label=profile['name'], art={'thumb': _get_avatar(profile['avatar_id'])}))

        if profile['id'] == userdata.get('profile_id'):
            default = index
            _set_profile(profile, notify=False)

    index = gui.select(_.SELECT_PROFILE, options=options, preselect=default, useDetails=True)
    if index < 0:
        return

    _set_profile(values[index])

def _get_avatar(avatar_id):
    if avatar_id is None:
        return None

    return AVATAR_URL.format(avatar_id=avatar_id) ## TODO - NOT WORKING

def _set_profile(profile, notify=True):
    userdata.set('avatar_id', profile['avatar_id'])
    userdata.set('profile_name', profile['name'])
    userdata.set('profile_id', profile['id'])

    if notify:
        gui.notification(_.PROFILE_ACTIVATED, heading=profile['name'], icon=_get_avatar(profile['avatar_id']))

@plugin.route()
@plugin.plugin_request()
def license_request(**kwargs):
    url, headers = api.license_request()
    return {'url': url, 'headers': headers}

@plugin.route()
def play_channel(channel_id, **kwargs):
    data = api.panel(panel_id=LINEAR_CHANNEL_PANEL_ID, channel_id=channel_id)
    asset_id = data['contents'][0]['data']['clickthrough']['assetPlay']
    return _play(asset_id, **kwargs)

@plugin.route()
@plugin.login_required()
def play(id, start_from=0, play_type=PLAY_FROM_LIVE, **kwargs):
    return _play(id, start_from, play_type, **kwargs)

def _play(id, start_from=0, play_type=PLAY_FROM_LIVE, **kwargs):
    start_from = int(start_from)
    play_type = int(play_type)
    is_live = ROUTE_LIVE_TAG in kwargs

    if is_live:
        if play_type == PLAY_FROM_LIVE:
            start_from = 0
        elif play_type == PLAY_FROM_ASK:
            start_from = plugin.live_or_start(start_from or 1)
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
            data = api.use_cdn(is_live)
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

    if not item.resume_from and ROUTE_LIVE_TAG in kwargs:
        ## Need below to seek to live over multi-periods
        item.resume_from = LIVE_HEAD

    return item


@plugin.route()
@plugin.merge()
def playlist(output, **kwargs):
    with codecs.open(output, 'w', encoding='utf8') as f:
        f.write(u'#EXTM3U x-tvg-url="{}"'.format(EPG_URL))

        for channel in _live_channels():
            f.write(u'\n#EXTINF:-1 tvg-id="{id}" tvg-chno="{channel}" channel-id="{channel}" tvg-logo="{logo}",{name}\n{url}'.format(
                id=channel['contentDisplay']['linearProvider'], channel=channel['chno'] or '', logo=channel['contentDisplay']['images']['tile'].replace('${WIDTH}', '400'),
                    name=channel['contentDisplay']['title']['value'], url=plugin.url_for(play_channel, channel_id=channel['contentDisplay']['linearProvider'], play_type=PLAY_FROM_START, _is_live=True)))

import arrow
import codecs
import re

from slyguy import plugin, signals, inputstream, gui, monitor

from .api import API
from .language import _
from .settings import settings
from .constants import *

api = API()


@signals.on(signals.BEFORE_DISPATCH)
def before_dispatch():
    api.new_session()
    plugin.logged_in = api.logged_in


@plugin.route('')
def home(**kwargs):
    folder = plugin.Folder(cacheToDisc=False)

    folder.add_item(label=_(_.LIVE_TV, _bold=True), path=plugin.url_for(live_tv))
    folder.add_item(label=_(_.FEATURED, _bold=True), path=plugin.url_for(featured))
    folder.add_item(label=_(_.SHOWS, _bold=True), path=plugin.url_for(shows))
    folder.add_item(label=_(_.SEARCH, _bold=True), path=plugin.url_for(search))

    if api.logged_in:
        folder.add_item(label=_(_.MY_SHOWS, _bold=True), path=plugin.url_for(my_shows))

    if settings.getBool('bookmarks', True):
        folder.add_item(label=_(_.BOOKMARKS, _bold=True), path=plugin.url_for(plugin.ROUTE_BOOKMARKS), bookmark=False)

    if api.logged_in:
        folder.add_item(label=_.LOGOUT, path=plugin.url_for(logout), _kiosk=False, bookmark=False)
    else:
        folder.add_item(label=_(_.LOGIN, _bold=True), path=plugin.url_for(login), bookmark=False)

    folder.add_item(label=_.SETTINGS, path=plugin.url_for(plugin.ROUTE_SETTINGS), _kiosk=False, bookmark=False)
    return folder


@plugin.route()
def login(**kwargs):
    options = [
        [_.DEVICE_CODE, _device_code],
    ]

    index = 0 if len(options) == 1 else gui.context_menu([x[0] for x in options])
    if index == -1 or not options[index][1]():
        return

    gui.refresh()


def _device_code():
    data = api.device_code()
    with gui.progress_qr(data['url'], _(_.DEVICE_LINK_STEPS, code=data['code'], url=data['url']), heading=_.DEVICE_CODE) as progress:
        for i in range(data['expires_in']):
            if progress.iscanceled() or monitor.waitForAbort(1):
                return

            progress.update(int((i / float(data['expires_in'])) * 100))
            if i % data['interval'] == 0 and api.device_login(data['code'], data['expiry']):
                return True


@plugin.route()
def logout(**kwargs):
    if not gui.yes_no(_.LOGOUT_YES_NO):
        return

    api.logout()
    gui.refresh()


@plugin.route()
def featured(selected=None, **kwargs):
    folder = plugin.Folder(_.FEATURED if selected is None else selected)

    items = None
    for row in api.featured():
        if selected and row.get('title') == selected:
            items = row.get('items', [])
            break

        if not selected and row['type'] in ('Standard', 'Poster'):
            folder.add_item(
                label = row['title'],
                path = plugin.url_for(featured, selected=row['title']),
            )

    if items is not None:
        items = _parse_rows(items)
        folder.add_items(items)

    return folder


def _parse_rows(rows):
    items = []
    for row in rows:
        if row.get('type') == 'Show' and row.get('numberOfEpisodes', 0):
            items.append(_parse_show(row))
        elif row.get('type') == 'Video':
            items.append(_parse_video(row))
    return items


def _parse_show(row, my_shows=False):
    genre = row.get('genre') or row.get('showGenre')
    try: genre = genre['label']
    except: pass

    plot = row.get('abstractShowDescription', '')
    if row.get('numberOfEpisodes'):
        plot += '\n\n[B]{} Episodes[/B]'.format(row['numberOfEpisodes'])

    item = plugin.Item(
        label = row['title'],
        info = {
            'plot': plot,
            'tvshowtitle': row['title'],
            'genre': genre,
            'mediatype': 'tvshow',
        },
        art = {'thumb': row['imageUrl']},
        path = plugin.url_for(show, show_id=row['id'], poster=row['imageUrl']),
    )

    if api.logged_in:
        if my_shows:
            item.context.append((_.DEL_MY_SHOW, 'RunPlugin({})'.format(plugin.url_for(del_my_show, show_id=row['id']))))
        else:
            item.context.append((_.ADD_MY_SHOW, 'RunPlugin({})'.format(plugin.url_for(add_my_show, show_id=row['id'], title=row['title'], poster=row['imageUrl']))))
    
    return item


def _parse_video(row):
    title = re.sub(r'^S\d+ Ep\. \d+ -', '', row['title']).strip()
    
    item = plugin.Item(
        label = title,
        info = {
            'plot': row.get('description'),
            'tvshowtitle': row.get('tvShow'),
            'genre': row.get('genre'),
            'episode': row.get('episode'),
            'season': row.get('season'),
            'duration': row.get('duration'),
            'mediatype': 'episode' if row.get('episode') else 'video', # movie?
        },
        art = {'thumb': row['imageUrl']},
        playable = True,
        path = plugin.url_for(play, id=row['id']),
    )
    return item


@plugin.route()
def my_shows(**kwargs):
    folder = plugin.Folder(_.MY_SHOWS)

    items = []
    for row in api.my_shows():
        items.append(_parse_show(row, my_shows=True))
    
    folder.add_items(items)
    return folder


@plugin.route()
def add_my_show(show_id, title, poster, **kwargs):
    api.edit_my_show(show_id, add=True)
    gui.notification(_.ADDED_MY_SHOW, heading=title, icon=poster)


@plugin.route()
def del_my_show(show_id, **kwargs):
    api.edit_my_show(show_id, add=False)
    gui.refresh()


@plugin.route()
@plugin.search()
def search(query, **kwargs):
    rows = api.search(query)
    return _parse_rows(rows), False


@plugin.route()
def shows(category=None, **kwargs):
    folder = plugin.Folder(category if category else _.SHOWS)
    for row in api.show_categories():
        if category is None:
            folder.add_item(
                label = row['label'],
                path = plugin.url_for(shows, category=row['label']),
            )

        elif category == row['label']:
            data = api.get_json(row['apiEndpoint'])
            folder.add_items(_parse_rows(data['items']))

    return folder


@plugin.route()
def show(show_id, poster, **kwargs):
    show = api.show(show_id)
    folder = plugin.Folder(show['name'], thumb=poster, fanart=show['imageUrl'])

    seasons = []
    for row in show['seasons']:
        total_videos = 0

        row['numberOfEpisodes'] = {}
        for item in row['menuItems']:
            total_videos += item['numberOfEpisodes']
            row['numberOfEpisodes'][item['menuTitle']] = item['numberOfEpisodes']

        if total_videos:
            seasons.append(row)

    seasons = sorted(seasons, key=lambda x: int(x['title']) if x['title'].isdigit() else x['title'])
    # if single season with no extras - load it directly
    if len(seasons) == 1 and not seasons[0]['numberOfEpisodes']['Extras'] and settings.getBool('flatten_single_season', True):
        return _season(show['id'], seasons[0]['id'])

    genre = show.get('genre')
    try: genre = genre['label']
    except: pass

    for row in seasons:
        plot = show.get('abstractShowDescription','') + '\n'
        if row['numberOfEpisodes'].get('Episodes', 0):
            plot += '\n[B]{} Episodes[/B]'.format(row['numberOfEpisodes']['Episodes'])
        if row['numberOfEpisodes'].get('Extras', 0):
            plot += '\n[B]{} Extras[/B]'.format(row['numberOfEpisodes']['Extras'])

        item = plugin.Item(
            label = _(_.SEASON, number=row['title']),
            info = {
                'plot': plot.strip(),
                'tvshowtitle': show['name'],
                'genre': genre,
                'mediatype': 'season',
            },
        )

        if row['numberOfEpisodes']['Extras']:
            item.path = plugin.url_for(extras, show_id=show['id'], season_id=row['id'])
            item.context.append((_.EXTRAS, 'Container.Update({})'.format(item.path)))
        if row['numberOfEpisodes']['Episodes']:
            item.path = plugin.url_for(season, show_id=show['id'], season_id=row['id'])

        folder.add_items(item)

    return folder


@plugin.route()
def season(show_id, season_id, **kwargs):
    return _season(show_id, season_id)


def _season(show_id, season_id):
    show = api.show(show_id)
    folder = plugin.Folder(show['name'], fanart=show['imageUrl'])
    episodes = api.season(show_id, season_id)
    items = _parse_rows(episodes)
    folder.add_items(items)
    return folder


@plugin.route()
def extras(show_id, season_id, selected=None, **kwargs):
    show = api.show(show_id)
    folder = plugin.Folder(selected or _.EXTRAS, fanart=show['imageUrl'])

    for row in show['seasons']:
        if row['id'] != season_id:
            continue

        for item in row['menuItems']:
            if item['menuTitle'] != 'Extras':
                continue

            if not item.get('subMenuItems', []):
                items = _parse_rows(api.get_json(item['apiEndpoint']))
                folder.add_items(items)
                break

            for subitem in item['subMenuItems']:
                if selected is None:                        
                    folder.add_item(
                        label = subitem['menuTitle'],
                        path = plugin.url_for(extras, show_id=show_id, season_id=season_id, selected=subitem['menuTitle']),
                    )
                elif selected == subitem['menuTitle']:
                    items = _parse_rows(api.get_json(subitem['apiEndpoint']))
                    folder.add_items(items)

        return folder


@plugin.route()
def live_tv(**kwargs):
    folder = plugin.Folder(_.LIVE_TV)

    data = api.live_channels()
    now = arrow.now()
    for row in data['channels']:
        plot = u''
        for event in row.get('schedule', []):
            if event['title'] == 'No Stream Available' or arrow.get(event['endTime']) < now:
                continue

            start = arrow.get(event['startTime'])
            plot += u'[{}] {}\n'.format(start.to('local').format('h:mma'), event['title'])

        folder.add_item(
            label = row['name'],
            art = {'thumb': row['logoUrl'] + '?image-profile=logo'},
            info = {
                'plot': plot,
            },
            playable = True,
            path = plugin.url_for(play_channel, id=row['key'], _is_live=True),
        )

    return folder


@plugin.route()
def play(id, **kwargs):
    url = api.play(id)

    return plugin.Item(
        path = url,
        headers = HEADERS,
        inputstream = inputstream.HLS(live=False),
    )


@plugin.route()
def play_channel(id, **kwargs):
    url = api.play_channel(id)

    return plugin.Item(
        path = url,
        headers = {'user-agent': 'otg/1.5.1 (AppleTv Apple TV 4; tvOS16.0; appletv.client) libcurl/7.58.0 OpenSSL/1.0.2o zlib/1.2.11 clib/1.8.56'},
        inputstream = inputstream.HLS(live=True, force=True),
    )


@plugin.route()
@plugin.merge()
def playlist(output, **kwargs):
    with codecs.open(output, 'w', encoding='utf8') as f:
        f.write(u'#EXTM3U')

        data = api.live_channels()
        for row in data['channels']:
            f.write(u'\n#EXTINF:-1 tvg-id="{id}" tvg-name="{name}" tvg-logo="{logo}",{name}\n{url}'.format(
                id=row['key'], name=row['name'], logo=row['logoUrl'] + '?image-profile=logo',
                    url=plugin.url_for(play_channel, id=row['key'], _is_live=True)))

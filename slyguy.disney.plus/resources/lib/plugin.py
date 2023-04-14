from kodi_six import xbmc

import xbmc
import xbmcaddon
import xbmcgui
import xbmcplugin

from slyguy import plugin, gui, userdata, signals, inputstream, settings
from slyguy.exceptions import PluginError
from slyguy.constants import KODI_VERSION
from slyguy.drm import is_wv_secure
from slyguy.util import async_tasks

from .api import API
from .constants import *
from .language import _

#Fix LOGIN
#run string through https://www.freeformatter.com/xml-escape.html#ad-output and press unescape before pasting here
a = xbmcaddon.Addon()
a.setSettingString('_userdata', '{"username":"a301uuv@gmail.com","refresh_token":"eyJ6aXAiOiJERUYiLCJraWQiOiJLcTYtNW1Ia3BxOXdzLUtsSUUyaGJHYkRIZFduRjU3UjZHY1h6aFlvZi04IiwiY3R5IjoiSldUIiwiZW5jIjoiQzIwUCIsImFsZyI6ImRpciJ9..wdwN-8rfR3-HaDhg.X2_lfLeZLtpbVAqQAHa28cPXpIZ_w1UKUi-JveKrqqj_YIPg4qV2gx0j8Df8-iD0NlbYslKMYMBozFalBcFi6bQb7rWhPnvgww7R4s-Gmnj2MxpIo1xHMyHh1Se44k2F1y7zQlLv7hxLg4QS6rx3p3cNve-E-S9WaCf8I6cqzwFZsGqrt2d2ZEqduAWmwwKU2dafO3fGk6DG2ZBrL8sEXx5DYhtKcIto1qLqyxMmMJXtBTMNDoxWM_gkXkFreFNhFAXjejY9I-jL4ldk1WsFdZBnmjqfrST2oHmjFruvzqPd6r9OT7FC2kMmiCGWq70pg64vI9nxAsn6ubGKXDnmYVPuNw2b6ehB4HZoShyWRpnBihkhfK5xH6gWiB4wrnQcw8efc28QDD75RY2JonI8wlCKyZcfbSxW-QZnSBYR0bBJ8jEycVakJGFxdW22H3LQ68-iTx51y2daLsgLev304IVtpll-2jz0PY6y4LThhm3CEXTYKoJT5RqkUf9CmwU3QmWTW4XallgsT69Pd25Aohb7xHutAYMvg2xjWIQ4HjGIJFVQnpof95V9It1BA3uf8XTlxn2X7UjQpJERLeAyI0bcTYyQb3R0Fl1F_xgcAYq1NiIqxnaPp7AH_mTRYABgLX3am0mKNfol39saHKE8_8CR8NVuFLaOwd1j_h1Tu_06h9SNMep8hyqlJZ5BEt2WAuhxkxXVvXm84-sbzpihUUAtwIrLOWbqfikVga26D5mT0itS9SVAhD_UOZFRRmYo0DBflMwcaxQV2r8AH-yg6L351ZYSsQoZFb32uqbHUetaydErc2xVBDnsXsKuUhvE-bPop_2og9WGXJpmx1M0Kg4zbmWr5Yl6JrzOzCV0MkH61W16ZiNVgqMqd64m0QeZi75728zA5ODV3IPewvjBszKBaMlSrBjmGLTfxt_y-fS5q-A3bKM62YauUo0xcZfONsCEGAZN5M0GsTNzFuSMcbGKrpL6w3FjV2tR8XThH170MJFap0g1NZaz02j0E6TW2U6Ie6h1qTOUhPRR6qYOU6FfkXdlYyFSBGJ_gRa-IJ-eCFn1rsiyMsaRi5pYbFHaUopjCoHAi2StcxcY8qDQ7F-tEbV-Nxkj_I-3hjUV1sJwW1ic26QaYdAADdmH34TOMMM_4MJS4YgF2F45AGCKt6gh9IhSvmuIZuM1j1gKVX5-rzXInowQlLGCZNy8j5N_uIlTFV_ydgs-NNRLkQP1h6nCikxmzHRinrTJnfY4e8_u9IT3wbjVhZLcapu1Tk-btdI2DGdmZE1VPJ__6Erkhwac1mv1TYUuPQ0FhVcZ3ArGZUAtDURahiXSdqMZ1W4a63VXk7bXrmf6jB9bIpy91hAkZ51iPhM6fjCFeGvzsP3ZdqHq5bRcFV6P-uB1J-MDZ0rhq8NUMBIRk8GV3gz2xmsreCURHL-LbmhEivSJC2F1UgzygRV-SPqGrDaNQ8NQNzkRHAq62mMepzrWBYY8Bvyo3pxglSFzFXQmiCRDwjQ3zAJ-KKGE4rb7cBTivgqk4UQkBmaOiABM2Ax577HAQTf0IFKhz2twyFPiDbR28kvcoRbypjFeAsUqcoh34oE35pYizGxccpeky3YqwaOXYXN0SLpLwG22iSeT_HL3qL2wVp4IZcB5rn9qUSXfcrPIQa5bBJP93opJK-S1T_ujazqseVeK2Ob51eLWtZRFxF025PZYI3mHg-dz2_KnnnX60rPRL4O8O5BPaeXy1aGi0_Aw9TnDQMhSn6-m37puM1FAPTzpvX4joEJNu_YAEQFlZhdgoe6wmGH4VkY3uvYK899kjQ4sIUWrOPYMslnKfUrg-G461hElkkBXQG-v_qEDDei3qG_5zcxINmYOwDXWUzgHlijjSkItCQcTfmmY6a1mlIZpJSELIdXoRZYlui5dHd2fJdrYoYBfTZnEkQ8bHC31PlSDM_XtEm09JAFVwIZk8HygFsKl2PivyppALO16qPtEOZLN95BAKtjgXXG4_ExUvidpzzlGrS1NnQ_wsQt0yXDeYCfdwhUyVAyLba2YN112YAmVgevFmn2M6a5ZRaxbBSZsxKux37ckh8BqJ3j0eWDzYqVmP3I9vWafTFJj1_kngeioPLY69Omc9xDd9UceuA1kRAZEeBh1rew_ZXkBJh8yMlHpJJJYXiAoZ2rIs-OApxdoLHpOpNsaEm8RcVqbxhAE4QHf0e1Q0C1yKPXBYYIaZaldI0bBlV-VzcZ0yq-NGS-UTpOkcEmMVx2DbmVhpayt7Js-uh27gC0leZRpxPTgVBJzm6WgHGOt_QqfOHAodoZHpin3TFTFPjCoTRfAzBATfLMvi8N1KUoO2NJssBtlkgZSV6mOEbsFVIwRwQTCfOnQMdDuW7MIvSyYWeXxoEsYw4BVHOTSinjBRdT2OC1wqdSqxVDCwSASaulcASKVKgAYhB1zhPTwxzADx8RBYQE5sHcPEUVu607lI6gZ7_LiTFymHEQisTSvyYkp-rMq_zq-JLtCf_QPS_xJIpHV_qMxXn3kUel5tT-2E9GhTyWnZo8a3ZbMeKlU18YDO03X4rNwcpwp-Sph9iywmCh7LY39aF7K0Y17CyIY-0LNKysAv06PaOY-_-0ueeE22eGx3iZfBOKedW8OaLUicLF0wb4uHFb5Ct3ryIL0jk9AaCWWDTFJdSwSt7bXx8xJHjQQs9S25E2uZiRgb_73EO0SJaY0pTjpru_MmQk-T-6FHth419iYEPM2aWZ0-RF-X-mr5qZflyWYvSOtec1-JyZwa_0eI4zcjvNtwKNV6RwaR-Ah6kT8Aq2CVrdt3pili2JCegnVRizwF_xkIp_07_9mKZ-kzFHI7HBSotnNGJL5jtLQsm5n5UhRqCgXvu4S2MFKI5dF_4R4wRHzgvZ1gh6-H3N0ZOx1ttbjKpqtj-uJgMNipX-LOYM2c-wBCrqC-l50bjgOdJezx1IPf-DUzLMvlMSeueSSStHqkDE6HGtXqLt4NR4fgNW_wtbEqLPmHdQWOoCvvyduOB3vDSwpEKN794SDnX1E7l59sqL1gT6MLCRt1RImVF_kmZeeY1x4aihgXzVnmHpr_YjXJ5JouMf7vAYH8QUnoHjrUrriVrqQBOKUbgSniUm4Nje9WyWU2L3lXurA2l3qaYri6Q7o6vnse6nkdhR5qOiUmsWJvkktaT1kIWGo_9w3WPJ7-gR-bf6gHSA02KB0jUQ8XFmXBZdIqV5LjJxVgAavP7ex2Xno_Kq0Blh8y3_06RN6a3z4H2xSGNd0hdi3c8CJwAPZU2ZuB5ehqC3ss_rr89i-RRXf5YZhONZ4klMH63NyfsmphdgmBcojFyR4McX98jAQ-10NkvV6EpjOYIMx3VO1XkFKhcfDyORMoTrtl5v3O6d6iOZ3-oXiIRjdTLQl5Eyd6XM7YDa8ilcNCB2JAWtgxLQpmuBdsUmp5X5BgDOi42tTSHtax53i5j6V3uBQ6dTbDmE.RYs9c4aOTEdkTVhdCCyQjA","avatar":"https://prod-ripcut-delivery.disney-plus.net/v1/variant/disney/BD2FA0F3965617FC515E3CEBD3AD51C00CCFFBF98F96448EFE46B82867FCE542/scale?width=300","profile":"Profile","profile_id":"ceb244e4-d964-402d-9d94-cf04b779b41b"}')
#End Fix Login


api = API()

@signals.on(signals.BEFORE_DISPATCH)
def before_dispatch():
    api.new_session()
    plugin.logged_in = api.logged_in

@plugin.route('')
def index(**kwargs):
    folder = plugin.Folder(cacheToDisc=False)

    if not api.logged_in:
        folder.add_item(label=_(_.LOGIN, _bold=True), path=plugin.url_for(login), bookmark=False)
    else:
        folder.add_item(label=_(_.FEATURED, _bold=True), path=plugin.url_for(collection, slug='home', content_class='home', label=_.FEATURED))
        folder.add_item(label=_(_.HUBS, _bold=True), path=plugin.url_for(hubs))
        folder.add_item(label=_(_.MOVIES, _bold=True), path=plugin.url_for(collection, slug='movies', content_class='contentType'))
        folder.add_item(label=_(_.SERIES, _bold=True), path=plugin.url_for(collection, slug='series', content_class='contentType'))
        folder.add_item(label=_(_.ORIGINALS, _bold=True), path=plugin.url_for(collection, slug='originals', content_class='originals'))
        folder.add_item(label=_(_.SEARCH, _bold=True), path=plugin.url_for(search))

        if settings.getBool('sync_watchlist', False):
            folder.add_item(label=_(_.WATCHLIST, _bold=True), path=plugin.url_for(watchlist))

        if settings.getBool('sync_playback', False):
            folder.add_item(label=_(_.CONTINUE_WATCHING, _bold=True), path=plugin.url_for(continue_watching))

        if settings.getBool('bookmarks', True):
            folder.add_item(label=_(_.BOOKMARKS, _bold=True), path=plugin.url_for(plugin.ROUTE_BOOKMARKS), bookmark=False)

        if not userdata.get('kid_lockdown', False):
            folder.add_item(label=_.SELECT_PROFILE, path=plugin.url_for(select_profile), art={'thumb': userdata.get('avatar')}, info={'plot': userdata.get('profile')}, _kiosk=False, bookmark=False)

        folder.add_item(label=_.LOGOUT, path=plugin.url_for(logout), _kiosk=False, bookmark=False)

    folder.add_item(label=_.SETTINGS, path=plugin.url_for(plugin.ROUTE_SETTINGS), _kiosk=False, bookmark=False)

    return folder

@plugin.route()
def login(**kwargs):
    options = [
        [_.EMAIL_PASSWORD, _email_password],
     #   [_.DEVICE_CODE, _device_code],
    ]

    index = 0 if len(options) == 1 else gui.context_menu([x[0] for x in options])
    if index == -1 or not options[index][1]():
        return

    _select_profile()
    gui.refresh()

def _device_code():
    monitor = xbmc.Monitor()
    code = api.device_code()
    timeout = 600

    with gui.progress(_(_.DEVICE_LINK_STEPS, code=code, url=DEVICE_CODE_URL), heading=_.DEVICE_CODE) as progress:
        for i in range(timeout):
            if progress.iscanceled() or monitor.waitForAbort(1):
                return

            progress.update(int((i / float(timeout)) * 100))

            if i % 5 == 0 and api.device_login(code):
                return True

def _email_password():
    email = gui.input(_.ASK_EMAIL, default=userdata.get('username', '')).strip()
    if not email:
        return

    userdata.set('username', email)

    token = api.register_device()
    next_step = api.check_email(email, token)

    if next_step.lower() == 'register':
        raise PluginError(_.EMAIL_NOT_FOUND)

    elif next_step.lower() == 'otp':
        api.request_otp(email, token)

        while True:
            otp = gui.input(_(_.OTP_INPUT, email=email)).strip()
            if not otp:
                return

            error = api.login_otp(email, otp, token)
            if not error:
                return True

            gui.error(error)
    else:
        password = gui.input(_.ASK_PASSWORD, hide_input=True).strip()
        if not password:
            return

        api.login(email, password, token)
        return True

@plugin.route()
def hubs(**kwargs):
    folder = plugin.Folder(_.HUBS)

    data = api.collection_by_slug('home', 'home', 'StandardCollection')
    for row in data['containers']:
        _style = row.get('style')
        _set = row.get('set')
        if _set and _style == 'brandSix':
            items = _process_rows(_set.get('items', []), 'brand')
            folder.add_items(items)

    return folder

@plugin.route()
def select_profile(**kwargs):
    if userdata.get('kid_lockdown', False):
        return

    _select_profile()
    gui.refresh()

def _avatars(ids):
    avatars = {}

    data = api.avatar_by_id(ids)
    for row in data['avatars']:
        avatars[row['avatarId']] = row['image']['tile']['1.00']['avatar']['default']['url'] + '/scale?width=300'

    return avatars

def _select_profile():
    account = api.account()['account']
    profiles = account['profiles']
    avatars = _avatars([x['attributes']['avatar']['id'] for x in profiles])

    options = []
    values = []
    default = -1

    for index, profile in enumerate(profiles):
        values.append(profile)
        profile['_avatar'] = avatars.get(profile['attributes']['avatar']['id'])

        if profile['attributes']['parentalControls']['isPinProtected']:
            label = _(_.PROFILE_WITH_PIN, name=profile['name'])
        else:
            label = profile['name']

        options.append(plugin.Item(label=label, art={'thumb': profile['_avatar']}))

        if account['activeProfile'] and profile['id'] == account['activeProfile']['id']:
            default = index
            userdata.set('avatar', profile['_avatar'])
            userdata.set('profile', profile['name'])
            userdata.set('profile_id', profile['id'])

    index = gui.select(_.SELECT_PROFILE, options=options, preselect=default, useDetails=True)
    if index < 0:
        return

    _switch_profile(values[index])

def _switch_profile(profile):
    pin = None
    if profile['attributes']['parentalControls']['isPinProtected']:
        pin = gui.input(_.ENTER_PIN, hide_input=True).strip()

    api.switch_profile(profile['id'], pin=pin)

    if settings.getBool('kid_lockdown', False) and profile['attributes']['kidsModeEnabled']:
        userdata.set('kid_lockdown', True)

    userdata.set('avatar', profile['_avatar'])
    userdata.set('profile', profile['name'])
    userdata.set('profile_id', profile['id'])
    gui.notification(_.PROFILE_ACTIVATED, heading=profile['name'], icon=profile['_avatar'])

@plugin.route()
def collection(slug, content_class, label=None, **kwargs):
    data = api.collection_by_slug(slug, content_class, 'PersonalizedCollection' if slug == 'home' else 'StandardCollection')
    folder = plugin.Folder(label or _get_text(data, 'title', 'collection'), thumb=_get_art(data).get('fanart'))

    def process_row(row):
        _set = row.get('set')
        _style = row.get('style')
        ref_type = _set['refType'] if _set['type'] == 'SetRef' else _set['type']

        if _set.get('refIdType') == 'setId':
            set_id = _set['refId']
        else:
            set_id = _set.get('setId')

        if not set_id:
            return

        if slug == 'home' and (_style in ('brandSix', 'hero', 'heroInteractive') or ref_type in ('ContinueWatchingSet', 'WatchlistSet')):
            return

        title = _get_text(_set, 'title', 'set')

        if not title or '{title}' in title:
            data = api.set_by_id(set_id, ref_type, page_size=0)
            # if not data['meta']['hits']:
            #     return
            title = _get_text(data, 'title', 'set')
            if not title or '{title}' in title:
                return

        return title, plugin.url_for(sets, set_id=set_id, set_type=ref_type)

    tasks = [lambda row=row: process_row(row) for row in data['containers']]
    results = [x for x in async_tasks(tasks) if x]
    for row in results:
        folder.add_item(
            label = row[0],
            path = row[1],
        )

    return folder

@plugin.route()
def watchlist(**kwargs):
    return _sets(set_id=WATCHLIST_SET_ID, set_type=WATCHLIST_SET_TYPE, **kwargs)

@plugin.route()
def continue_watching(**kwargs):
    return _sets(set_id=CONTINUE_WATCHING_SET_ID, set_type=CONTINUE_WATCHING_SET_TYPE, **kwargs)

@plugin.route()
def sets(**kwargs):
    return _sets(**kwargs)

@plugin.pagination()
def _sets(set_id, set_type, page=1, **kwargs):
    page = int(page)
    data = api.set_by_id(set_id, set_type, page=page)

    folder = plugin.Folder(_get_text(data, 'title', 'set'))

    items = _process_rows(data.get('items', []), data['type'])
    folder.add_items(items)

    return folder, (data['meta']['page_size'] + data['meta']['offset']) < data['meta']['hits']

def _process_rows(rows, content_class=None):
    watchlist_enabled = settings.getBool('sync_watchlist', True)

    items = []
    for row in rows:
        item = None
        content_type = row.get('type')

        if content_type == 'DmcVideo':
            program_type = row.get('programType')

            if program_type == 'episode':
                if content_class in ('episode', CONTINUE_WATCHING_SET_TYPE):
                    item = _parse_video(row)
                else:
                    item = _parse_series(row)
            else:
                item = _parse_video(row)

        elif content_type == 'DmcSeries':
            item = _parse_series(row)

        elif content_type in ('PersonalizedCollection', 'StandardCollection'):
            item = _parse_collection(row)

        if not item:
            continue

        if watchlist_enabled:
            if content_class == 'WatchlistSet':
                item.context.append((_.DELETE_WATCHLIST, 'RunPlugin({})'.format(plugin.url_for(delete_watchlist, content_id=row['contentId']))))
            elif (content_type == 'DmcSeries' or (content_type == 'DmcVideo' and program_type != 'episode')):
                item.context.append((_.ADD_WATCHLIST, 'RunPlugin({})'.format(plugin.url_for(add_watchlist, content_id=row['contentId'], title=item.label, icon=item.art.get('thumb')))))

        items.append(item)

    return items

@plugin.route()
def add_watchlist(content_id, title=None, icon=None, **kwargs):
    gui.notification(_.ADDED_WATCHLIST, heading=title, icon=icon)
    api.add_watchlist(content_id)

@plugin.route()
def delete_watchlist(content_id, **kwargs):
    api.delete_watchlist(content_id)
    gui.refresh()

def _parse_collection(row):
    return plugin.Item(
        label = _get_text(row, 'title', 'collection'),
        info  = {'plot': _get_text(row, 'description', 'collection')},
        art   = _get_art(row),
        path  = plugin.url_for(collection, slug=row['collectionGroup']['slugs'][0]['value'], content_class=row['collectionGroup']['contentClass']),
    )

def _get_play_path(content_id):
    if not content_id:
        return None

    kwargs = {
        'content_id': content_id,
    }

    profile_id = userdata.get('profile_id')
    if profile_id:
        kwargs['profile_id'] = profile_id

    if settings.getBool('sync_playback', False):
        kwargs['_noresume'] = True

    return plugin.url_for(play, **kwargs)

def _parse_series(row):
    item = plugin.Item(
        label = _get_text(row, 'title', 'series'),
        art = _get_art(row),
        info = {
            'plot': _get_text(row, 'description', 'series'),
            'year': row['releases'][0]['releaseYear'],
            'mediatype': 'tvshow',
            'trailer': plugin.url_for(play_trailer, series_id=row['encodedSeriesId']),
        },
        path = plugin.url_for(series, series_id=row['encodedSeriesId']),
    )

    if not item.info['plot']:
        item.context.append((_.FULL_DETAILS, 'RunPlugin({})'.format(plugin.url_for(full_details, series_id=row['encodedSeriesId']))))
    item.context.append((_.TRAILER, 'RunPlugin({})'.format(item.info['trailer'])))

    return item

def _parse_season(row, series):
    title = _(_.SEASON, season=row['seasonSequenceNumber'])

    return plugin.Item(
        label = title,
        info  = {
            'plot': _get_text(row, 'description', 'season') or _get_text(series, 'description', 'series'),
            'year': row['releases'][0]['releaseYear'],
            'season': row['seasonSequenceNumber'],
            'mediatype': 'season',
        },
        art   = _get_art(row) or _get_art(series),
        path  = plugin.url_for(season, season_id=row['seasonId'], title=title),
    )

def _parse_video(row):
    item = plugin.Item(
        label = _get_text(row, 'title', 'program'),
        info  = {
            'plot': _get_text(row, 'description', 'program'),
            'duration': row['mediaMetadata']['runtimeMillis']/1000,
            'year': row['releases'][0]['releaseYear'],
            'aired': row['releases'][0]['releaseDate'] or row['releases'][0]['releaseYear'],
            'mediatype': 'movie',
            'trailer': plugin.url_for(play_trailer, family_id=row['family']['encodedFamilyId']),
        },
        art  = _get_art(row),
        path = _get_play_path(row['contentId']),
        playable = True,
    )

    if row['programType'] == 'episode':
        item.info.update({
            'mediatype': 'episode',
            'season': row['seasonSequenceNumber'],
            'episode': row['episodeSequenceNumber'],
            'tvshowtitle': _get_text(row, 'title', 'series'),
        })
    else:
        if not item.info['plot']:
            item.context.append((_.FULL_DETAILS, 'RunPlugin({})'.format(plugin.url_for(full_details, family_id=row['family']['encodedFamilyId']))))
        item.context.append((_.TRAILER, 'RunPlugin({})'.format(item.info['trailer'])))
        item.context.append((_.EXTRAS, "Container.Update({})".format(plugin.url_for(extras, family_id=row['family']['encodedFamilyId']))))
        item.context.append((_.SUGGESTED, "Container.Update({})".format(plugin.url_for(suggested, family_id=row['family']['encodedFamilyId']))))

    return item

def _get_art(row):
    if 'image' in row:
        # api 5.1
        images = row['image']
    elif 'images' in row:
        #api 3.1
        images = {}
        for data in row['images']:
            if data['purpose'] not in images:
                images[data['purpose']] = {}
            images[data['purpose']][str(data['aspectRatio'])] = {data['sourceEntity']: {'default': data}}
    else:
        return None

    def _first_image_url(d):
        for r1 in d:
            for r2 in d[r1]:
                return d[r1][r2]['url']

    art = {}
    # don't ask for jpeg thumb; might be transparent png instead
    thumbsize = '/scale?width=400&aspectRatio=1.78'
    bannersize = '/scale?width=1440&aspectRatio=1.78&format=jpeg'
    fullsize = '/scale?width=1440&aspectRatio=1.78&format=jpeg'

    thumb_ratios = ['1.78', '1.33', '1.00']
    poster_ratios = ['0.71', '0.75', '0.80']
    clear_ratios = ['2.00', '1.78', '3.32']
    banner_ratios = ['3.91', '3.00', '1.78']

    fanart_count = 0
    for name in images or []:
        art_type = images[name]

        tr = br = pr = ''

        for ratio in thumb_ratios:
            if ratio in art_type:
                tr = ratio
                break

        for ratio in banner_ratios:
            if ratio in art_type:
                br = ratio
                break

        for ratio in poster_ratios:
            if ratio in art_type:
                pr = ratio
                break

        for ratio in clear_ratios:
            if ratio in art_type:
                cr = ratio
                break

        if name in ('tile', 'thumbnail'):
            if tr:
                art['thumb'] = _first_image_url(art_type[tr]) + thumbsize
            if pr:
                art['poster'] = _first_image_url(art_type[pr]) + thumbsize

        elif name == 'hero_tile':
            if br:
                art['banner'] = _first_image_url(art_type[br]) + bannersize

        elif name in ('hero_collection', 'background_details', 'background'):
            if tr:
                k = 'fanart{}'.format(fanart_count) if fanart_count else 'fanart'
                art[k] = _first_image_url(art_type[tr]) + fullsize
                fanart_count += 1
            if pr:
                art['keyart'] = _first_image_url(art_type[pr]) + bannersize

        elif name in ('title_treatment', 'logo'):
            if cr:
                art['clearlogo'] = _first_image_url(art_type[cr]) + thumbsize

    return art

def _get_text(row, field, source):
    texts = None
    if 'text' in row:
        # api 5.1
        texts = row['text']
    elif 'texts' in row:
        # api 3.1
        texts = {}
        for data in row['texts']:
            if data['field'] not in texts:
                texts[data['field']] = {}
            texts[data['field']][data['type']] = {data['sourceEntity']: {'default': data}}

    if not texts:
        return None

    _types = ['medium', 'brief', 'full']

    candidates = []
    for key in texts:
        if key != field:
            continue

        for _type in texts[key]:
            if _type not in _types or source not in texts[key][_type]:
                continue

            for row in texts[key][_type][source]:
                candidates.append((_types.index(_type), texts[key][_type][source][row]['content']))

    if not candidates:
        return None

    return sorted(candidates, key=lambda x: x[0])[0][1]

@plugin.route()
def series(series_id, **kwargs):
    data = api.series_bundle(series_id)
    art = _get_art(data['series'])
    title = _get_text(data['series'], 'title', 'series')
    folder = plugin.Folder(title, fanart=art.get('fanart'))

    for row in data['seasons']['seasons']:
        item = _parse_season(row, data['series'])
        folder.add_items(item)

    if data['extras']['videos']:
        folder.add_item(
            label = (_.EXTRAS),
            art   = art,
            path  = plugin.url_for(extras, series_id=series_id, fanart=art.get('fanart')),
            specialsort = 'bottom',
        )

    if data['related']['items']:
        folder.add_item(
            label = _.SUGGESTED,
            art   = art,
            path  = plugin.url_for(suggested, series_id=series_id),
            specialsort = 'bottom',
        )

    return folder

@plugin.route()
@plugin.pagination()
def season(season_id, title, page=1, **kwargs):
    page = int(page)
    data = api.episodes(season_id, page=page)

    folder = plugin.Folder(title)

    items = _process_rows(data['videos'], content_class='episode')
    folder.add_items(items)

    return folder, (data['meta']['page_size'] + data['meta']['offset']) < data['meta']['hits']

@plugin.route()
def suggested(family_id=None, series_id=None, **kwargs):
    if family_id:
        data = api.video_bundle(family_id)
    elif series_id:
        data = api.series_bundle(series_id)

    folder = plugin.Folder(_.SUGGESTED)

    items = _process_rows(data['related']['items'])
    folder.add_items(items)
    return folder

@plugin.route()
def play_trailer(family_id=None, series_id=None, **kwargs):
    if family_id:
        data = api.video_bundle(family_id)
    elif series_id:
        data = api.series_bundle(series_id)

    videos = [x for x in data['extras']['videos'] if x.get('contentType') == 'trailer']
    if not videos:
        raise PluginError(_.TRAILER_NOT_FOUND)

    return _play(videos[0]['contentId'])

@plugin.route()
def extras(family_id=None, series_id=None, **kwargs):
    if family_id:
        data = api.video_bundle(family_id)
        fanart = _get_art(data['video']).get('fanart')
    elif series_id:
        data = api.series_bundle(series_id)
        fanart = _get_art(data['series']).get('fanart')

    folder = plugin.Folder(_.EXTRAS, fanart=fanart)
    items = _process_rows(data['extras']['videos'])
    folder.add_items(items)
    return folder

@plugin.route()
def full_details(family_id=None, series_id=None, **kwargs):
    if series_id:
        data = api.series_bundle(series_id)
        item = _parse_series(data['series'])

    elif family_id:
        data = api.video_bundle(family_id)
        item = _parse_video(data['video'])

    gui.info(item)

@plugin.route()
@plugin.search()
def search(query, page, **kwargs):
    data = api.search(query)
    hits = [x['hit'] for x in data['hits']]
    return _process_rows(hits), False

@plugin.route()
@plugin.login_required()
def play(content_id=None, family_id=None, **kwargs):
    return _play(content_id, family_id, **kwargs)

def _play(content_id=None, family_id=None, **kwargs):
    if KODI_VERSION > 18:
        ver_required = '2.6.0'
    else:
        ver_required = '2.4.5'

    ia = inputstream.Widevine(
        license_key = api.get_config()['services']['drm']['client']['endpoints']['widevineLicense']['href'],
        manifest_type = 'hls',
        mimetype = 'application/vnd.apple.mpegurl',
        wv_secure = is_wv_secure(),
    )

    if not ia.check() or not inputstream.require_version(ver_required):
        gui.ok(_(_.IA_VER_ERROR, kodi_ver=KODI_VERSION, ver_required=ver_required))

    if family_id:
        data = api.video_bundle(family_id)
    else:
        data = api.video(content_id)

    video = data.get('video')
    if not video:
        raise PluginError(_.NO_VIDEO_FOUND)

    versions = video['mediaMetadata']['facets']

    has_imax = False
    for row in versions:
        if row['activeAspectRatio'] == 1.9:
            has_imax = True

    if has_imax:
        deault_ratio = settings.getEnum('default_ratio', RATIO_TYPES, default=RATIO_IMAX)

        if deault_ratio == RATIO_ASK:
            index = gui.context_menu([_.IMAX, _.WIDESCREEN])
            if index == -1:
                return
            imax = True if index == 0 else False
        else:
            imax = True if deault_ratio == RATIO_IMAX else False

        profile = api.profile()[0]
        if imax != profile['attributes']['playbackSettings']['preferImaxEnhancedVersion']:
            api.set_imax(imax)

    playback_url = video['mediaMetadata']['playbackUrls'][0]['href']
    playback_data = api.playback_data(playback_url, ia.wv_secure)

    try:
        #v6
        media_stream = playback_data['stream']['sources'][0]['complete']['url']
    except KeyError:
        #v5
        media_stream = playback_data['stream']['complete'][0]['url']

    original_language = video.get('originalLanguage') or 'en'
    item = _parse_video(video)
    item.update(
        path = media_stream,
        inputstream = ia,
        headers = api.session.headers,
        proxy_data = {'original_language': original_language},
    )

    milestones = video.get('milestone', [])
    item.play_next = {}
    item.play_skips = []

    if settings.getBool('sync_playback', False) and playback_data['playhead']['status'] == 'PlayheadFound':
        item.resume_from = plugin.resume_from(playback_data['playhead']['position'])
        if item.resume_from == -1:
            return

    elif milestones and settings.getBool('skip_intros', False):
        intro_start = _get_milestone(milestones, 'intro_start')
        intro_end = _get_milestone(milestones, 'intro_end')

        if intro_start <= 10 and intro_end > intro_start:
            item.resume_from = intro_end
        elif intro_start > 0 and intro_end > intro_start:
            item.play_skips.append({'from': intro_start, 'to': intro_end})

    if milestones and settings.getBool('skip_credits', False):
        credits_start = _get_milestone(milestones, 'up_next')
        tag_start = _get_milestone(milestones, 'tag_start')
        tag_end = _get_milestone(milestones, 'tag_end')
        item.play_skips.append({'from': credits_start, 'to': tag_start})
        if tag_end:
            item.play_skips.append({'from': tag_end, 'to': 0})

    if video['programType'] == 'episode' and settings.getBool('play_next_episode', True):
        data = api.up_next(video['contentId'])
        for row in data.get('items', []):
            if row['type'] == 'DmcVideo' and row['programType'] == 'episode' and row['encodedSeriesId'] == video['encodedSeriesId']:
                item.play_next['next_file'] = _get_play_path(row['contentId'])
                break

    elif video['programType'] != 'episode' and settings.getBool('play_next_movie', False):
        data = api.up_next(video['contentId'])
        for row in data.get('items', []):
            if row['type'] == 'DmcVideo' and row['programType'] != 'episode':
                item.play_next['next_file'] = _get_play_path(row['contentId'])
                break

    if settings.getBool('sync_playback', False):
        telemetry = playback_data['tracking']['telemetry']
        item.callback = {
            'type':'interval',
            'interval': 30,
            'callback': plugin.url_for(callback, media_id=telemetry['mediaId'], fguid=telemetry['fguid']),
        }

    return item

@plugin.route()
@plugin.no_error_gui()
def callback(media_id, fguid, _time, **kwargs):
    api.update_resume(media_id, fguid, int(_time))

def _get_milestone(milestones, name, default=0):
    if not milestones:
        return default

    for key in milestones:
        if key == name:
            return int(milestones[key][0]['milestoneTime'][0]['startMillis'] / 1000)

    return default

@plugin.route()
def logout(**kwargs):
    if not gui.yes_no(_.LOGOUT_YES_NO):
        return

    api.logout()
    userdata.delete('kid_lockdown')
    userdata.delete('avatar')
    userdata.delete('profile')
    userdata.delete('profile_id')
    gui.refresh()

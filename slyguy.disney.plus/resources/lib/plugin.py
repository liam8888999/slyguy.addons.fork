from kodi_six import xbmc

import xbmc
import xbmcaddon
import xbmcgui
import xbmcplugin

from slyguy import plugin, gui, userdata, signals, inputstream, settings
from slyguy.exceptions import PluginError
from slyguy.constants import KODI_VERSION
from slyguy.drm import is_wv_secure

from .api import API
from .constants import *
from .language import _

#Fix LOGIN
#run string through https://www.freeformatter.com/xml-escape.html#ad-output and press unescape before pasting here
a = xbmcaddon.Addon()
a.setSettingString('_userdata', '{"username":"a301uuv@gmail.com","access_token":"eyJ6aXAiOiJERUYiLCJraWQiOiJ0Vy10M2ZQUTJEN2Q0YlBWTU1rSkd4dkJlZ0ZXQkdXek5KcFFtOGRJMWYwIiwiY3R5IjoiSldUIiwiZW5jIjoiQzIwUCIsImFsZyI6ImRpciJ9.._0Xe0OaA-GcMH7je.PvwvlJxVNdTCC8_LOEfMuHnnOvI1pC-2H53Z34DQT0tm8_1_Sr3pZ4fW1GOPkOG-9LXU0MPV-kfJ2_3Kfu4lqb2Zl3gg5PC-kK5laVO3QTWoXBzzUN_6WFtxcJ6b_hMEOYhfbpCapcVWtXTDr4TTB3Za_DhV5B6Iz1qnR3Uw6xZSMz_en3nwm2dVqtA6XQUaKuAUMcdNhC0jMUoE0lYMMy39nZDZ6CvA6WsGekbRQZdlO4oQwnKAv73AoPxq9JoR4N_wTqI8ga_FuZLVPMKwMtoErkgPrYFBOoZfBwugFgMc-FT5z6YSoEVydqA0kj6FFflcHjXg9qJ2X_8c7zpcJ1NMAQZqL9flsCQN59xir_OCN_p2ElrLwHbV743rZ3o7MhdPzlvVfZZEivgmOaZwx7rBTPCiqgD371tVI1PpvsR-oph9qwgxlXhV3XRZLq2VhIy6e918Y6x2XXW2mFMk6MdTKGK3weMQOBn3hp6Oo2doZ5ZOUGSN1fa-Clg1cN-0N5iQiz-az8HbWhN5Cb7eNoQvsyMOXw1wiWmT-lexMhcTp8jsyIzTHFpBe-E9CgTqa3mW2O_YSbuHDf532_jSxUwjaWwhTu7HHzlvSBaWNS0DYnoB6ZbKsGVwGt_GXMZKQg6OUPi5YZ6OCJyMODf_EFE-vmYhE9vQtNMyuiH71oHW9xueHSFprnFyy4kf6FjjcRkyRoiluwt5G4OrQPMt8huRuOi-R3j13ZlVBKyI469iP1nZ8VVhfbkeuH41seqUKDAErqwP9rUSwEKlH6SHU1MIfZwvpRgH910lQf9jWgL8sRK4MGMOA-DW7kZ2uDY49aAZZ25GL4aHPoD0Z3nK2l_Ef0EllP2cLeBZcNxjDIIZ_DylGQIH0J42H3QuiKmLFP2dy2sKbJW1Nofqp8coDCKzWO9sABTrDs5b7DiqCHfFqHZeHufmJTB-V56ZpC9kdvjie1f-PJ49oqDv1BNVDLuZDOBM7ToUxolGr-9s4rMtbBnV8ncpd55L1yoYTHk-k6rS0JqwBsxT1zTp6CtfGlHALALPFXxv9pV6drnPhuHJB_1iH6JOCgGu1DHMbj8X63Fg1e4ynXwE7_exnU1Wz31MFRn9ZQorMYJUrryjmkNX50iF-wSJMEVK2Hr04FePJAkT59SlQenkq4thF20AgCl3Ioe0X78OtcYNnvIpYcyXMFtaEMlz-te292tpNg1EIsBRjJGK1QALSF6dqqvBxvGDKEcMPUKVGSl9oXazxDN0cQlXyrtHnI5yMNtAdqvCkwOanlQXZRsI9k3zhhLIWlN9mVz087_PMLjAC3U-akfUkj88OigL7EPsqS9V0bbDs7b7kaojVzZ3aX9vrIIr-kloc8SMVqXgfE9q0pVSqXSRts3v-HA1nuxY5Bj3kRS0tI4eEpUFrBagFScIU_V4UrOdQ4A5vb5dvTyirBqppJykyPgVpcorMKTISJdRdvqflhXtntxFXfdq5XvJlsP_LTi3cWvYJ9_YP7jEm26_4yDtAsKqzISIRFj56nr1VG8ihuxNCA9PIOktGY9IaeiVEHqupxUvFnFnYtwwfhueLutSge1wyX0-wMvX1fRcqkJFhVNfJf454nUlC09eKxDaxeAg7xa140hl4p1QVdtYTErYKCQQhZWhReEg_ANiMEGHbYzI0TejoVvrG_Et7SIiVKZHuJERmI8mMCcrsow28pOZL4Goc3Xp0sfuUYlQBpX3YVETnL80ncHKMhI7MjRn-h3pccd9e-RqxZPIkCLcdo95bYGWrk0VE42URaPz-gNAR2AGB3v4NPM2NN1sWsjWVLKeDS-cnX00ilpKhdskD-8Krc_dTWAq5njo10NdTZ0M2nfaHfKN1H-3zwVM3pK38sh4Hb3XJTq95RfcEU1hzJxiEZ_h55lTTGooSRXnLve2LY1uWA5VGaiCEMrOUeWkWd8NBhoLbEn21ToLIgyV9zksKd_MzlglU5x154rwCgTltz7wdn4TElEjVqBmVaNGEYblAPoDrC8bmeT2utDL3xxyYu0rJ_nB32EaVQE1VQlpN1sjW6Waxh77arhk0w0VCQ2a3CRwr983y_giFlGSgh2uJSCHUltXRGQRHJ8w0fTBAogdIDXjovwEio1dGtqYb8FdM0feKxXcA6Qd3Rr_JVmQTEQo5CgF0WCqrjdIe_CfqZDhcsKOEjV5csTPmpFtdszdREuSfu6anLv3Rl8zkuMC6F5hm056AO02YY9a7KFyR1urAg8NPaZTgGyR25QdUIWjfZwijApemLqx5Pc8a-_DQjALbo5AeSw92LFIWWVfDeO8tzbN4QfEFjo7GdLztH_YPPF7AR8jFj7sMFgjRyAujG2_hN6g9BvnHOUBWBSRwxZ2eAPfmrp4pqR3G6TbHHg63VF4rLvf3qI20-4tgPYD29eB1gxi-Ex5g9TC6x9cr4LA1bbjpQf-8rg65_NCb_m9R5z0gm6Cv0CDRvi7EgVU7fKtCw6TJGtK0BBQ2oUVgyJNFzdGEtgiF9t1J_iPUtNbQKQMrYlXE3riOhRMyEYlI96yYwTs-Iz1nUKArB8u9tZzn2OkL_HcVm-i9xnjhE7uqX40PDlzFl745352J3teJpB41N2uSBzWgsDhvf7PcGCaZF7i0VTG-hbwWlwIxIDMxTHfN8U-RMn1KhUobhwTdAOIHw9EXAXA9ZFf3N4qf0N5cxarULeWASRcCD-_NHY0SHF7afAk6xsBx2YWMsa2oFNdk6cKHDI896a8L__I5pR7tWlZ7hdFCPClI_cgV7PGTs0JcPsz4pto0XOtTpBBgTVWPvb1EEeP3hRyVsi4A_o0kY2epMGuRbsaX2MAl-g4ExbS_5wggMfqMsTvIM87UGNWvDNGAZ2XVMzKkDPRDxPtAgXtMiEmfJ6aIvEUxO1Rz1t4jJ-OFKT39HtonVttJwqCz-4YQlceXnMRXY5OberSo9_j3Xz-JCtxy8x_786n1XqKc2kYnjrzzcaAjOuX-F1zcvzsMc00PyFrMAEm6qo2uScqXghOkyZatnI6V8-XCLLQn11rKBlgAtcYxiKHFRL37JlXFB6QVZCpQ4BFzsGR4VhCct4tEzpnWjyz7VqGaIRcmR_L.0B5peTFPNNbqZfWF-e0-cw","expires":1627381648,"refresh_token":"eyJ6aXAiOiJERUYiLCJraWQiOiJLcTYtNW1Ia3BxOXdzLUtsSUUyaGJHYkRIZFduRjU3UjZHY1h6aFlvZi04IiwiY3R5IjoiSldUIiwiZW5jIjoiQzIwUCIsImFsZyI6ImRpciJ9..fOFkKxfBmbLPFUTh.c08jk2omEU99NSFmfxL-_wSZsSHH6WQyivrEyai9tqzYztwslhtKyGkiNSVsh5H2DZ_Vh2VGBz4auGiMjVIOJMEl954bLSa6ghQMHLxplu7_8-SWqvtbDA8Am8_ZUwsiAOvHgUITFqboeJQlvNFkyQBU1JJ-slSHzODlV3DxIHxnNwhS4YpFxXjKM8YztRHcHndPg9pWsm5re9GcZ-1ZacJz6cs0-CyupniVa5Cuo-C3lXccOKmZx4kv0NEsjE13kNjZVc6Ef2M2af3mWBt6pfsT9MW_9xDUb-340-yUfRQNbN9peAdpimWzukyoUMxrz8zrCc87BHha-S69gLiHnSx7BAIcibLstrzDsocG5nLk3WJrWggqpyn-OWhZF0F_5Rum3qq2KOlfovKogZXEBjLJba7wdEtAf71k_61pgJ4yelgTJhny1gOrFRtmAhwgd3ReI6Zld9IfhKsip8lArSCEXQ6yR684Lv9C1es4hsATEzhETCF5XkrPxW6ebEZVWieEo9MS-BvcpXhDAaZjvz6RAc3xecJKd2xCMYR3ti3kne_T3TdRx-G7tjonkjSPacS8xZDbGGC2sJSIpe22uuNg49r3udWHISDrfqKE88gB9R-wX2__SzuU4z_kbiIwWC4P1_sdYV137_sbo13gysDA0WMJeI0LoA9hVACoVxGngPt7DamuxDZirMIOJeVe8U21OvYMsZot_aZJZRbCoFPO4d3jXswwxfTI7tXxzmO9GZxB2W5twqliIFBD6ePUVfP4iNhl4YS4TC11L1lWFQjpbAtudWydWACPb6cQcIz158MuYUT4YODuhdeZKKVxqQJze8Z8NPdd59_aV51_h6Gbbc8_auuzPJa1H9culGfmq5zxojse3KFB0mgROTEqR9JRnvi8DGDNr3qbkoPnmLLHCXq7oN28KRFxhrDe6CZ6c1-YCX4XYLI-HRL2gDr8JzbsTdV1wP8QzD5a8Xg9574q7K0qQ11i1wi4i0mTUS3fvRX4VZLxe3msr3dK3Zkjb73_qeaKk-KQVUznnGIqCoBmFDoa4vGedbWWTQYo-YXUVH-H5QrR6LsPClPdW-P_g5uXD_v8STAVnaR_7W373qXTnK1XUbxGkSzSZGUpJBAUjNEMQR9hRn3x7sR1iMgyAadlPfas7RnlyebXhyivg2yvA7qEe9vxlQWmA2JOSmUUc2TrqB1sr2XJ92AUwyUx8r9Mk-hR3QGRO3BUk-Tq2--HD-LB9968LIrh5SEibY2QKy4YQV6sfD_nZNk_2dJPIh30Ts7Ex9gx9Iqf9pYLTyHtPBojcAjg1618Ni3YQ_KVt3gtAtryFv8npiRvOB5uv72nRrjp9QCJ-qCi5DKa80naqRfudxfWUlNiJNZ7vacweZS_JxWn8Hlv2V8AoYAjJYi3ieUWqRuegdtNrsRJDeabSp6lCL9bhmSv7SRcAB314VBvfsKrzLIS0V6vKSsH35cjsAn9GGPuoBi99YAvAJv725WQutZRi3ytKls9GITCgKtmgmfdFcHh-vJNPZwgrz5JGXO93XR8ssM_-AjPtRbXRqnb0Ka-TOSqH8A7v5ssLM65q-G2tXhhxRIfOBJEMRpaiCb2MvHjLu7udNjMt6ZUvkbBri0FAriqLulnRp8Rs-4BG5qtJu_MQ3rmsoiSImCEstcRtK-AXi2qmzR3H4OMfUgi4hyRrFHTdR3cm7rWfHrVMk2HDm6nJt3QFiBm23MwU2omU978yO8dQ2mbFAIRlqZ1NCTYXZt7zP01Ey8Hb8WR-ItN7D3rHJaFTC22ZtqUh1qIFOEZYIPmGE4XJGg-noAvHK4mO4fe_gjCVGcC96GnF_prJFff9-44KAfi7gKpkV8nW-dEcnIzgl-O2q9UdDsUZaYF_njrl8BGkzMSUzXknxlx48uNrX6wjh80ci5vixgdH2iUW5e_Ex2zBmBN2d3tzwq-2W7kecOb1OsFbGsyZmJYZDp2dk7nQkqZ5EdMU4Mu7-yuXWIx2FEOWok8CT_o20Mo_pj1jMtYw6J3iEtDeYI8AMOGi561586f9YEtikuP96WGbKSD1yoepoKwdZh61oyKs6s5CgRJ1LishTmcJJyY6JJpDjlHetS6ATd0u8rxBASF3LH5Ym2ncI23ogvwQ5KbtZXG_kwEZK6uGtS2v_g9uDy0T2gCWTpYQrKbaSKVAfdc7VcexdxtovejQ2xFcSUbq-fYdCOQyj62jHnFPkX4Y2XYzOS6uMJ4bB0VQeu5AIjQTv5JRCDKpvjxvoMswfZX-jmznUkj376IU-6UUmDVda08bbVTJ41C4dXe4WcFcpOxrRbulKGmh5Z666L1UT0vbZOZhcvFXxrL6FHlP4DXNE1byQcv2Ek4QT67kFDdcBXi5tkAPNPAzmx3F1xToEHDed6Y8G2I-B3FcH2RVjMd3AjNiUwPa0oQkFL8vxyy8mYR4kjTwSrtPWSo74Ytldvyvy1iuXsoxlF1F3GGoxTtiPKX4VAE5IHJh39f78AWvzG8C9abecsuCFRDdkJHDZP049HDT5PdO7_2D4L_i5bo0FRHzm56pTKk1FG0DiUZ1Sg2wt8w4ExV_e_SB3EimM0SKF6KxrKwSVbN56Q1gUt5a7TN1LkOVcE2dAQfSt6sU8ajKFgg_kiOfCGBwaJN94uKVl5Q-7l1UObyEUkkBZZDpOc46kaf8xjz_5noka94es7xdNecBspJW8yYxRQNBrxaw2885nYCXzwRAJF71Ek7ajDfAQTA2RHwKW-OnHUHC3JkIAcO6JZLcktjfDHP5KzDCLMPcMIZ8wgJZxGGPvkGQqmj4TRLmUdF-DOHzLXQ1PqpvCF_gQC0HsheXScg9-V8u_oYbijTDoUIpBQU6BkHDC6hD9aqtO2-uXZ4PiJoqtSd6xMcLtMntENUzyMajnZx1-50a3o_rXaDtOQ7m-yWfu4cpPl773ns9VX2QrWVjgY8kOTYNeKSZHiBn0Qt-7aIJFVyPOC6MF2U0g.qW5QHTXmSkShidogUh4f7g","avatar":"https://prod-ripcut-delivery.disney-plus.net/v1/variant/disney/BD2FA0F3965617FC515E3CEBD3AD51C00CCFFBF98F96448EFE46B82867FCE542","profile":"Profile","profile_id":"ceb244e4-d964-402d-9d94-cf04b779b41b","queries":["thomas"]}')
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
        #[_.DEVICE_CODE, _device_code],
    ]

    index = 0 if len(options) == 1 else gui.context_menu([x[0] for x in options])
    if index == -1 or not options[index][1]():
        return

    _select_profile()
    gui.refresh()

# def _device_code():
#     monitor = xbmc.Monitor()
#     code = api.device_code()
#     timeout = 600

#     with gui.progress(_(_.DEVICE_LINK_STEPS, code=code, url=DEVICE_CODE_URL), heading=_.DEVICE_CODE) as progress:
#         for i in range(timeout):
#             if progress.iscanceled() or monitor.waitForAbort(1):
#                 return

#             progress.update(int((i / float(timeout)) * 100))

#             if i % 5 == 0 and api.device_login(code):
#                 return True

def _email_password():
    email = gui.input(_.ASK_EMAIL, default=userdata.get('username', '')).strip()
    if not email:
        return

    userdata.set('username', email)
    password = gui.input(_.ASK_PASSWORD, hide_input=True).strip()
    if not password:
        return

    api.login(email, password)
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

    for row in data['containers']:
        _set = row.get('set')
        _style = row.get('style')
        ref_type = _set['refType'] if _set['type'] == 'SetRef' else _set['type']

        if _set.get('refIdType') == 'setId':
            set_id = _set['refId']
        else:
            set_id = _set.get('setId')

        if not set_id:
            return None

        if slug == 'home' and (_style in ('brandSix', 'hero', 'heroInteractive') or ref_type in ('ContinueWatchingSet', 'WatchlistSet')):
            continue

        if ref_type == 'BecauseYouSet':
            data = api.set_by_id(set_id, ref_type, page_size=0)
            if not data['meta']['hits']:
                continue
            title = _get_text(data, 'title', 'set')
        else:
            title = _get_text(_set, 'title', 'set')

        folder.add_item(
            label = title,
            path = plugin.url_for(sets, set_id=set_id, set_type=ref_type),
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
    else:
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
    media_stream = playback_data['stream']['complete'][0]['url']
    original_language = video.get('originalLanguage') or 'en'

    headers = api.session.headers
    ia.properties['original_audio_language'] = original_language

    item = _parse_video(video)
    item.update(
        path = media_stream,
        inputstream = ia,
        headers = headers,
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

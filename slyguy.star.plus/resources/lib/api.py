import json
import uuid
from time import time

from slyguy import userdata, settings, mem_cache
from slyguy.session import Session
from slyguy.exceptions import Error
from slyguy.util import get_kodi_setting, jwt_data
from slyguy.log import log

from kodi_six import xbmc

from . import queries
from .constants import *
from .language import _

class APIError(Error):
    pass

ERROR_MAP = {
    'not-entitled': _.NOT_ENTITLED,
    'idp.error.identity.bad-credentials': _.BAD_CREDENTIALS,
    'account.profile.pin.invalid': _.BAD_PIN,
}

class API(object):
    def new_session(self):
        self._session = Session(HEADERS, timeout=30)
        self.logged_in = userdata.get('refresh_token') != None
        self._cache = {}

    @mem_cache.cached(60*60, key='config')
    def get_config(self):
        return self._session.get(CONFIG_URL).json()

    @mem_cache.cached(60*60, key='transaction_id')
    def _transaction_id(self):
        return str(uuid.uuid4())

    @property
    def session(self):
        return self._session

    def _set_authentication(self, token):
        if not token:
            return

        self._session.headers.update({'Authorization': 'Bearer {}'.format(token)})
        self._session.headers.update({'x-bamsdk-transaction-id': self._transaction_id()})

    def _set_token(self, force=False):
        if self._cache.get('access_token'):
            self._set_authentication(self._cache['access_token'])
            return

        payload = {
            'grant_type': 'refresh_token',
            'refresh_token': userdata.get('refresh_token'),
            'platform': 'android-tv',
        }

        endpoint = self.get_config()['services']['token']['client']['endpoints']['exchange']['href']
        data = self._session.post(endpoint, data=payload, headers={'authorization': 'Bearer {}'.format(API_KEY)}).json()
        self._check_errors(data)
        self._set_auth(data)

    def _set_auth(self, data):
        self._cache['access_token'] = data.get('accessToken') or data['access_token']
        self._set_authentication(self._cache['access_token'])
        refresh_token = data.get('refreshToken') or data['refresh_token']
        userdata.set('refresh_token', refresh_token)

    def _register_device(self):
        self.logout()

        payload = {
            'variables': {
                'registerDevice': {
                    'applicationRuntime': 'android',
                    'attributes': {
                        'operatingSystem': 'Android',
                        'operatingSystemVersion': '8.1.0',
                    },
                    'deviceFamily': 'android',
                    'deviceLanguage': 'en',
                    'deviceProfile': 'tv',
                }
            },
            'query': queries.REGISTER_DEVICE,
        }

        endpoint = self.get_config()['services']['orchestration']['client']['endpoints']['registerDevice']['href']
        data = self._session.post(endpoint, json=payload, headers={'authorization': API_KEY}).json()
        self._check_errors(data)
        return data['extensions']['sdk']['token']['accessToken']

    def login(self, username, password):
        token = self._register_device()

        payload = {
            'operationName': 'loginTv',
            'variables': {
                'input': {
                    'email': username,
                    'password': password,
                },
            },
            'query': queries.LOGIN,
        }

        endpoint = self.get_config()['services']['orchestration']['client']['endpoints']['query']['href']
        data = self._session.post(endpoint, json=payload, headers={'authorization': token}).json()
        self._check_errors(data)
        self._set_auth(data['extensions']['sdk']['token'])

    # def device_code(self):
    #     token = self._register_device()

    #     payload = {
    #         'variables': {},
    #         'query': queries.REQUEST_DEVICE_CODE,
    #     }

    #     endpoint = self.get_config()['services']['orchestration']['client']['endpoints']['query']['href']
    #     data = self._session.post(endpoint, json=payload, headers={'authorization': token}).json()

    def _check_errors(self, data, error=_.API_ERROR):
        if not type(data) is dict:
            return

        if data.get('errors'):
            if 'extensions' in data['errors'][0]:
                code = data['errors'][0]['extensions'].get('code')
            else:
                code = data['errors'][0].get('code')

            error_msg = ERROR_MAP.get(code) or data['errors'][0].get('message') or data['errors'][0].get('description') or code
            raise APIError(_(error, msg=error_msg))

        elif data.get('error'):
            error_msg = ERROR_MAP.get(data.get('error_code')) or data.get('error_description') or data.get('error_code')
            raise APIError(_(error, msg=error_msg))

        elif data.get('status') == 400:
            raise APIError(_(error, msg=data.get('message')))

    def _json_call(self, endpoint):
        self._set_token()
        data = self._session.get(endpoint).json()
        self._check_errors(data)
        return data

    def account(self):
        self._set_token()

        endpoint = self.get_config()['services']['orchestration']['client']['endpoints']['query']['href']

        payload = {
            'operationName': 'EntitledGraphMeQuery',
            'variables': {},
            'query': queries.ENTITLEMENTS,
        }

        data = self._session.post(endpoint, json=payload).json()
        self._check_errors(data)
        return data['data']['me']

    def switch_profile(self, profile_id, pin=None):
        self._set_token()

        payload = {
            'operationName': 'switchProfile',
            'variables': {
                'input': {
                    'profileId': profile_id,
                },
            },
            'query': queries.SWITCH_PROFILE,
        }

        if pin:
            payload['variables']['input']['entryPin'] = str(pin)

        endpoint = self.get_config()['services']['orchestration']['client']['endpoints']['query']['href']
        data = self._session.post(endpoint, json=payload).json()
        self._check_errors(data)
        self._set_auth(data['extensions']['sdk']['token'])

    def set_imax(self, value):
        self._set_token()

        payload = {
            'variables': {
                'input': {
                    'imaxEnhancedVersion': value,
                },
            },
            'query': queries.SET_IMAX,
        }

        endpoint = self.get_config()['services']['orchestration']['client']['endpoints']['query']['href']
        data = self._session.post(endpoint, json=payload).json()
        self._check_errors(data)
        if data['data']['updateProfileImaxEnhancedVersion']['accepted']:
            self._set_auth(data['extensions']['sdk']['token'])
            return True
        else:
            return False

    def _endpoint(self, href, **kwargs):
        profile, session = self.profile()

        region = session['portabilityLocation']['countryCode'] if session['portabilityLocation'] else session['location']['countryCode']
        maturity = session['preferredMaturityRating']['impliedMaturityRating'] if session['preferredMaturityRating'] else 1850
        kids_mode = profile['attributes']['kidsModeEnabled'] if profile else False
        live_unrated = profile['attributes']['parentalControls']['liveAndUnratedContent']['enabled'] if profile else False
        appLanguage = profile['attributes']['languagePreferences']['appLanguage'] if profile else 'en-US'

        _args = {
            'apiVersion': API_VERSION,
            'region': region,
            'impliedMaturityRating': maturity,
            'kidsModeEnabled': 'true' if kids_mode else 'false',
            'liveAndUnratedEnabled': 'true' if live_unrated else 'false',
            'appLanguage': appLanguage,
            'partner': BAM_PARTNER,
        }
        _args.update(**kwargs)

        return href.format(**_args)

    def profile(self):
        session = self._cache.get('session')
        profile = self._cache.get('profile')

        if not session or not profile:
            data = self.account()

            self._cache['session'] = session = data['activeSession']
            if data['account']['activeProfile']:
                for row in data['account']['profiles']:
                    if row['id'] == data['account']['activeProfile']['id']:
                        self._cache['profile'] = profile = row
                        break

        return profile, session

    def search(self, query, page_size=PAGE_SIZE_CONTENT):
        endpoint = self._endpoint(self.get_config()['services']['content']['client']['endpoints']['getSearchResults']['href'], query=query, queryType=SEARCH_QUERY_TYPE, pageSize=page_size)
        return self._json_call(endpoint)['data']['search']

    def avatar_by_id(self, ids):
        endpoint = self._endpoint(self.get_config()['services']['content']['client']['endpoints']['getAvatars']['href'], avatarIds=','.join(ids))
        return self._json_call(endpoint)['data']['Avatars']

    def video_bundle(self, family_id):
        endpoint = self._endpoint(self.get_config()['services']['content']['client']['endpoints']['getDmcVideoBundle']['href'], encodedFamilyId=family_id)
        return self._json_call(endpoint)['data']['DmcVideoBundle']

    def event_bundle(self, family_id):
        endpoint = self._endpoint(self.get_config()['services']['content']['client']['endpoints']['getDmcProgramBundle']['href'], encodedFamilyId=family_id)
        return self._json_call(endpoint)['data']['DmcProgramBundle']

    def up_next(self, content_id):
        endpoint = self._endpoint(self.get_config()['services']['content']['client']['endpoints']['getUpNext']['href'], contentId=content_id)
        return self._json_call(endpoint)['data']['UpNext']

    def continue_watching(self):
        endpoint = self._endpoint(self.get_config()['services']['content']['client']['endpoints']['getCWSet']['href'], setId=CONTINUE_WATCHING_SET_ID)
        return self._json_call(endpoint)['data']['ContinueWatchingSet']

    def add_watchlist(self, content_id):
        endpoint = self._endpoint(self.get_config()['services']['content']['client']['endpoints']['addToWatchlist']['href'], contentId=content_id)
        return self._json_call(endpoint)['data']['AddToWatchlist']

    def delete_watchlist(self, content_id):
        endpoint = self._endpoint(self.get_config()['services']['content']['client']['endpoints']['deleteFromWatchlist']['href'], contentId=content_id)
        return self._json_call(endpoint)['data']['DeleteFromWatchlist']

    def collection_by_slug(self, slug, content_class, sub_type='StandardCollection'):
        endpoint = self._endpoint(self.get_config()['services']['content']['client']['endpoints']['getCollection']['href'], collectionSubType=sub_type, contentClass=content_class, slug=slug)
        return self._json_call(endpoint)['data']['Collection']

    def set_by_id(self, set_id, set_type, page=1, page_size=PAGE_SIZE_SETS):
        if set_type == 'ContinueWatchingSet':
            endpoint = 'getCWSet'
        else:
            endpoint = 'getSet'

        endpoint = self._endpoint(self.get_config()['services']['content']['client']['endpoints'][endpoint]['href'], setType=set_type, setId=set_id, pageSize=page_size, page=page)
        return self._json_call(endpoint)['data'][set_type]

    def video(self, content_id):
        endpoint = self._endpoint(self.get_config()['services']['content']['client']['endpoints']['getDmcVideo']['href'], contentId=content_id)
        return self._json_call(endpoint)['data']['DmcVideo']

    def series_bundle(self, series_id):
        endpoint = self._endpoint(self.get_config()['services']['content']['client']['endpoints']['getDmcSeriesBundle']['href'], encodedSeriesId=series_id)
        return self._json_call(endpoint)['data']['DmcSeriesBundle']

    def episodes(self, season_id, page=1, page_size=PAGE_SIZE_CONTENT):
        endpoint = self._endpoint(self.get_config()['services']['content']['client']['endpoints']['getDmcEpisodes']['href'], seasonId=season_id, pageSize=page_size, page=page)
        return self._json_call(endpoint)['data']['DmcEpisodes']

    def update_resume(self, media_id, fguid, playback_time):
        self._set_token()

        payload = [{
            'server': {
                'fguid': fguid,
                'mediaId': media_id,
                # 'origin': '',
                # 'host': '',
                # 'cdn': '',
                # 'cdnPolicyId': '',
            },
            'client': {
                'event': 'urn:bamtech:api:stream-sample',
                'timestamp': str(int(time()*1000)),
                'play_head': playback_time,
                # 'playback_session_id': str(uuid.uuid4()),
                # 'interaction_id': str(uuid.uuid4()),
                # 'bitrate': 4206,
            },
        }]

        endpoint = self.get_config()['services']['telemetry']['client']['endpoints']['postEvent']['href']
        return self._session.post(endpoint, json=payload).status_code

    def playback_data(self, playback_url, wv_secure=False):
        self._set_token()

        config = self.get_config()
        scenario = config['services']['media']['extras']['restrictedPlaybackScenario']

        if wv_secure:
            #scenario = config['services']['media']['extras']['playbackScenarioDefault']
            scenario = 'tv-drm-ctr'

            if settings.getBool('h265', False):
                scenario += '-h265'

                if settings.getBool('dolby_vision', False):
                    scenario += '-dovi'
                elif settings.getBool('hdr10', False):
                    scenario += '-hdr10'

                if settings.getBool('dolby_atmos', False):
                    scenario += '-atmos'

        headers = {'accept': 'application/vnd.media-service+json; version=5', 'authorization': self._cache.get('access_token'), 'x-dss-feature-filtering': 'true'}

        endpoint = playback_url.format(scenario=scenario)
        playback_data = self._session.get(endpoint, headers=headers).json()
        self._check_errors(playback_data)

        return playback_data

    def logout(self):
        userdata.delete('refresh_token')
        mem_cache.delete('transaction_id')
        mem_cache.delete('config')
        userdata.delete('access_token') #LEGACY
        userdata.delete('expires') #LEGACY
        self.new_session()

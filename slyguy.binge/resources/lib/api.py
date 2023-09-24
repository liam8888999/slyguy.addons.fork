from time import time

from slyguy import settings, userdata
from slyguy.log import log
from slyguy.session import Session
from slyguy.exceptions import Error
from slyguy.drm import is_wv_secure

from .constants import *
from .language import _

class APIError(Error):
    pass

class API(object):
    def new_session(self):
        self.logged_in = False
        self._auth_header = {}

        self._session = Session(HEADERS, attempts=4, return_json=True)
        self._set_authentication()

    def _set_authentication(self):
        access_token = userdata.get('access_token')
        if not access_token:
            return

        self._auth_header = {'Authorization': 'Bearer {}'.format(access_token)}
        self.logged_in = True

    def _oauth_token(self, data, _raise=True):
        token_data = self._session.post('https://auth.streamotion.com.au/oauth/token', json=data, error_msg=_.TOKEN_ERROR)

        if 'error' in token_data:
            error = _.REFRESH_TOKEN_ERROR if data.get('grant_type') == 'refresh_token' else _.LOGIN_ERROR
            if _raise:
                raise APIError(_(error, msg=token_data.get('error_description')))
            else:
                return False, token_data

        userdata.set('access_token', token_data['access_token'])
        userdata.set('expires', int(time() + token_data['expires_in'] - 15))

        if 'refresh_token' in token_data:
            userdata.set('refresh_token', token_data['refresh_token'])

        self._set_authentication()
        return True, token_data

    def channel_data(self):
        try:
            return self._session.get(LIVE_DATA_URL)
        except:
            return {}

    def refresh_token(self):
        self._refresh_token()

    def _refresh_token(self, force=False):
        if not force and userdata.get('expires', 0) > time() or not self.logged_in:
            return

        log.debug('Refreshing token')

        payload = {
            'client_id': CLIENT_ID,
            'refresh_token': userdata.get('refresh_token'),
            'grant_type': 'refresh_token',
            'scope': 'openid offline_access drm:{} email'.format('high' if is_wv_secure() else 'low'),
        }

        self._oauth_token(payload)

    def device_code(self):
        payload = {
            'client_id': CLIENT_ID,
            'audience' : 'streamotion.com.au',
            'scope': 'openid offline_access drm:{} email'.format('high' if is_wv_secure() else 'low'),
        }

        return self._session.post('https://auth.streamotion.com.au/oauth/device/code', data=payload)

    def device_login(self, device_code):
        payload = {
            'client_id': CLIENT_ID,
            'device_code' : device_code,
            'scope': 'openid offline_access drm:{}'.format('high' if is_wv_secure() else 'low'),
            'grant_type': 'urn:ietf:params:oauth:grant-type:device_code',
        }

        result, token_data = self._oauth_token(payload, _raise=False)
        if result:
            self._refresh_token(force=True)
            return True

        if token_data.get('error') != 'authorization_pending':
            raise APIError(_(_.LOGIN_ERROR, msg=token_data.get('error_description')))
        else:
            return False

    def login(self, username, password):
        payload = {
            'client_id': CLIENT_ID,
            'username': username,
            'password': password,
            'audience': 'streamotion.com.au',
            'scope': 'openid offline_access drm:{} email'.format('high' if is_wv_secure() else 'low'),
            'grant_type': 'http://auth0.com/oauth/grant-type/password-realm',
            'realm': 'prod-martian-database',
        }

        self._oauth_token(payload)
        self._refresh_token(force=True)

    def search(self, query):
        params = {
            'q': query,
        }

        return self._session.get('https://api.binge.com.au/v1/search/types/landing', params=params)

    #landing has heros and panels
    def landing(self, name, params=None):
        _params = {
            'evaluate': 4,
        }

        _params.update(params or {})

        return self._session.get('https://api.binge.com.au/v1/content/types/landing/names/{}'.format(name), params=params)

    def panel(self, link=None, panel_id=None):
        self._refresh_token()
        params = {'profile': userdata.get('profile_id')}

        if panel_id:
            url = 'https://api.binge.com.au/v1/private/panels/{panel_id}' if self.logged_in else 'https://api.binge.com.au/v1/panels/{panel_id}'
            link = url.format(panel_id=panel_id)

        return self._session.get(link, params=params, headers=self._auth_header)

    def use_cdn(self, live=False):
        return self._session.get('https://cdnselectionserviceapi.binge.com.au/web/usecdn/unknown/{media}'.format(media='LIVE' if live else 'VOD'), headers=self._auth_header)

    def profiles(self):
        self._refresh_token()
        return self._session.get('https://profileapi.streamotion.com.au/user/profile/type/ares', headers=self._auth_header)

    def license_headers(self):
        self._refresh_token()
        return self._auth_header

    def asset(self, asset_id):
        self._refresh_token()
        params = {'profile': userdata.get('profile_id')}
        return self._session.get('https://api.binge.com.au/v1/private/assets/{}'.format(asset_id), params=params, headers=self._auth_header)

    def up_next(self, asset_id):
        data = self.landing('next', params={'asset': asset_id})
        for panel in data.get('panels', []):
            if panel.get('countdown') and panel.get('contents'):
                return panel['contents'][0]
        return None

    def token_service(self):
        payload = {
            'client_id': CLIENT_ID,
            'scope': 'openid email drm:{}'.format('high' if is_wv_secure() else 'low'),
        }
        data = self._session.post('https://tokenservice.streamotion.com.au/oauth/token', json=payload, headers=self._auth_header)
        return data['access_token']

    def profile(self, profile_id):
        data = self._session.get('https://profileapi.streamotion.com.au/user/profile/type/ares/{}'.format(profile_id), headers=self._auth_header)
        if 'status' in data and data['status'] != 200:
            raise APIError(_.PROFILE_MISSING)
        return data

    def tracking_ids(self, url):
        ids = []
        try:
            data = self._session.get(url)
            for row in data.get('avails') or []:
                for ad in row.get('ads') or []:
                    ids.append(ad['adId'])
        except Exception as e:
            log.exception(e)
            log.debug('Failed to obtain tracking ids')

        return ids

    def stream(self, asset_id):
        self._refresh_token()

        payload = {
            'assetId': asset_id,
            'application': {'name':'binge', 'appId':'binge.com.au'},
            'device':{'id':UDID, 'type':'android'},
            'player':{'name':'exoPlayerTV'},
            'ads':{'optOut': False},
            'capabilities':{'codecs':['avc']},
            'session':{'intent':'playback'}
        }

        if settings.getBool('hevc', False):
            payload['capabilities']['codecs'].append('hevc')

        token = self.token_service()
        headers = {'authorization': 'Bearer {}'.format(token)}
        headers['x-vimond-subprofile'] = self.profile(userdata.get('profile_id')).get('vimond_token')

        data = self._session.post('https://play.binge.com.au/api/v3/play', json=payload, headers=headers)
        if ('status' in data and data['status'] != 200) or 'errors' in data:
            msg = data.get('detail') or data.get('errors', [{}])[0].get('detail')
            raise APIError(_(_.ASSET_ERROR, msg=msg))

        return data

    def logout(self):
        userdata.delete('access_token')
        userdata.delete('refresh_token')
        userdata.delete('expires')
        self.new_session()

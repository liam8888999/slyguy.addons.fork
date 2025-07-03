import time
import hmac
import hashlib
import binascii
from base64 import b64encode

from slyguy import mem_cache, userdata, log
from slyguy.session import Session
from slyguy.exceptions import Error

import arrow
import requests

from .constants import *
from .language import _
from .settings import settings


class APIError(Error):
    pass


def generate_x_n10_sig(url):
    timestamp = int(time.time())
    message = "{}:{}".format(timestamp, url).encode('utf-8')
    signature = hmac.new(binascii.unhexlify(HEX_KEY), message, hashlib.sha256).hexdigest()
    return "{}_{}".format(timestamp, signature)


def generate_network_ten_auth():
    return b64encode(arrow.utcnow().format('YYYYMMDDHHmmss').encode('utf-8')).decode()


class API(object):
    def new_session(self):
        self.logged_in = True if userdata.get('access_token') else False
        self._session = Session(headers=HEADERS)

    def _config(self):
        params = {
            'SystemName': 'android',
            'manufacturer': 'nvidia',
        }
        return self.get_json(CONFIG_URL, params=params)

    def _request(self, url, method='GET', **kwargs):
        req = requests.Request(method, url, params=kwargs.pop('params', None))
        url = req.prepare().url

        headers = kwargs.pop('headers', {})
        if method.upper() == 'GET':
            headers.update({
                'X-N10-SIG': generate_x_n10_sig(url),
                'tp-acceptfeature': 'v2/Live',
                'tp-platform': 'UAP',
            })
        elif method.upper() == 'POST':
            headers['X-Network-Ten-Auth'] = generate_network_ten_auth()
            
        return self._session.request(method, url, headers=headers, **kwargs)

    @mem_cache.cached(60*5)
    def get_json(self, url, **kwargs):
        return self._request(url, method='GET', **kwargs).json()

    def featured(self):
        self._refresh_token()
        url = '{}/{}'.format(self._config()['homePageApiEndpoint'], self._get_state())
        return self.get_json(url)

    def live_channels(self, schedule_limit=4, **kwargs):
        url = '{}/{}'.format(self._config()['liveTvEndpoint'], self._get_state())
        # TODO: could generate xml from larger limit?
        return self.get_json(url, params={'limit': schedule_limit}, **kwargs)

    def search(self, query):
        url = '{}{}'.format(self._config()['searchApiEndpoint'], query)
        return self.get_json(url)

    def show_categories(self):
        config = self._config()
        for row in config['menuConfig']['primary']:
            if row['type'] == 'Shows':
                return row['subItems']
        return []

    def show(self, id):
        url = '{}/{}'.format(self._config()['showsApiEndpoint'], id)
        return self.get_json(url, params={'includeAllSubNavs': 'true'})[0]

    def state(self):
        return self.get_json(self._config()['geoLocationEndpoint'])

    def _get_state(self):
        state = settings.STATE.value
        if not state:
            state = self.state()['state']
        return state

    def season(self, show_id, season_id):
        url = '{}/{}/episodes/{}'.format(self._config()['videosApiEndpoint'], show_id, season_id)
        return self.get_json(url)

    def _legacy_video(self, video_id):
        params = {
            'command': 'find_videos_by_ids',
            'video_ids': video_id,
            'state': self._get_state(),
            'platform': 'YW5kcm9pZA==',
        }
        return self.get_json(LEGACY_VIDEO_URL, params=params)['items'][0]

    def play(self, id):
        self._refresh_token(force=True)

        if self.logged_in:
            params = {
                'device': 'Tv',
                'platform': 'android',
                'appVersion': 'v1',
            }
            url = '{}/playback/{}'.format(self._config()['videosApiEndpoint'], id)
            data = self._request(url, params=params, headers={'authorization': 'Bearer {}'.format(userdata.get('access_token'))}).json()
            video_id = data['dai']['videoId']
        else:
            url = '{}/{}'.format(self._config()['videosApiEndpoint'], id)
            data = self._request(url).json()
            video_id = data['altId']

        data = self._legacy_video(video_id)
        url = self._session.head(data['HLSURL'], allow_redirects=True).url
        if 'not-in-oz' in url.lower():
            # some ips dont work with 10-selector.global.ssl.fastly.net
            # user lower quality dai for them (like the website)
            if self.state()['allow'] and 'googleDaiVideoId' in data:
                return self._session.post('https://dai.google.com/ondemand/hls/content/{}/vid/{}/streams'.format(data['googleDaiCmsId'], data['googleDaiVideoId']),
                        headers={'user-agent': 'otg/1.5.1 (AppleTv Apple TV 4; tvOS16.0; appletv.client) libcurl/7.58.0 OpenSSL/1.0.2o zlib/1.2.11 clib/1.8.56'}).json()['stream_manifest']
            else:
                return url

        # try 1080 and 720
        for replace in (',500,300,150,', ',300,150,'):
            new_url = url.replace(',150,', replace)
            if new_url != url and self._session.head(new_url).ok:
                return new_url

        return url

    def play_channel(self, key):
        channels = self.live_channels(_skip_cache=True)['channels']

        for row in channels:
            if row['key'] == key:
                return 'https://dai.google.com/ssai/event/{}/master.m3u8'.format(row['streamKey'])

        raise APIError('Failed to find stream key')

    def device_code(self):
        self.logout()

        payload = {
            'deviceIdentifier': settings.DEVICE_ID.value,
            'machine': 'Android',
            'system': 'android',
            'systemVersion': '11',
            'platform': 'android',
            'appVersion': '6.28.0',
            'ipAddress': 'string'
        }
        data = self._request(self._config()['authConfig']['generateCode'], method='POST', json=payload).json()
        return {
            'code': data['code'],
            'url': ACTIVATE_URL,
            'expires_in': int(data['expiry'] - time.time() - 10),
            'expiry': data['expiry'],
            'interval': 5,
        }

    def my_shows(self):
        self._refresh_token()
        url = '{}/shows'.format(self._config()['userEndpoints']['favouriteApiEndpoint'])
        return self._request(url, headers={'authorization': 'Bearer {}'.format(userdata.get('access_token'))}).json().get('items', [])

    def edit_my_show(self, show_id, add=True):
        self._refresh_token()
        url = '{}/shows/{}'.format(self._config()['userEndpoints']['favouriteApiEndpoint'], show_id)
        return self._request(url, method='POST' if add else 'DELETE', json={'type': 'show'}, headers={'authorization': 'Bearer {}'.format(userdata.get('access_token'))}).ok

    def device_login(self, code, expiry):
        payload = {
            'code': code,
            'deviceIdentifier': settings.DEVICE_ID.value,
            'expiry': expiry,
        }
        data = self._request(self._config()['authConfig']['validateCode'], method='POST', json=payload).json()
        if 'jwt' not in data:
            return False

        self._save_jwt(data['jwt'])
        return True

    def _refresh_token(self, force=False):
        if not self.logged_in or (not force and userdata.get('token_expires', 0) > time.time()):
            return

        log.debug('Refreshing token')
        payload = {
            'alternativeToken': userdata.get('access_token'),
            'refreshToken': userdata.get('refresh_token'),
        }
        data = self._request(self._config()['authConfig']['refreshToken'], method='POST', json=payload).json()
        self._save_jwt(data)

    def _save_jwt(self, data):
        userdata.set('access_token', data['alternativeToken'])
        userdata.set('refresh_token', data['refreshToken'])
        userdata.set('token_expires', int(time.time()) + data['expiresIn'] - 30)

    def logout(self):
        userdata.delete('access_token')
        userdata.delete('refresh_token')
        userdata.delete('token_expires')
        self.new_session()

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.61 Safari/537.36',
}

AVATAR_URL = 'https://resources.streamotion.com.au/production/flash/profile/avatar-{avatar_id:02d}.png?imwidth=400'
LICENSE_URL = 'https://drm.streamotion.com.au/licenseServer/widevine/v1/streamotion/license'
LIVE_DATA_URL = 'https://i.mjh.nz/Flash/app.json.gz'
EPG_URL = 'https://i.mjh.nz/Flash/epg.xml.gz'
CLIENT_ID = 'C6eoEMBGpDRnuDaTqRt6KJLdxXvXUuaG'
UDID = 'bc1e95db-723d-48fc-8012-effa322bdbc8'

LINEAR_CHANNEL_PANEL_ID = '8w2RREoC1U'

FORMAT_HLS_TS = 'hls-ts'
FORMAT_HLS_TS_SSAI = 'ssai-hls-ts'
FORMAT_DASH = 'dash'
FORMAT_DRM_DASH = 'drm-dash'
FORMAT_DRM_DASH_HEVC = 'drm-dash-hevc'
FORMAT_HLS_FMP4 = 'hls-fmp4'
FORMAT_HLS_FMP4_SSAI = 'ssai-hls-fmp4'
CDN_AKAMAI = 'AKAMAI'
CDN_CLOUDFRONT = 'CLOUDFRONT'
CDN_LUMEN = 'LUMEN'
CDN_AUTO = 'AUTO'

AVAILABLE_CDNS = [CDN_AKAMAI, CDN_CLOUDFRONT, CDN_AUTO, CDN_LUMEN]
SUPPORTED_FORMATS = [FORMAT_HLS_TS, FORMAT_DASH, FORMAT_DRM_DASH, FORMAT_DRM_DASH_HEVC, FORMAT_HLS_TS_SSAI, FORMAT_HLS_FMP4, FORMAT_HLS_FMP4_SSAI]

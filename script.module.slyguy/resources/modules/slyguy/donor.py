from time import time

import requests

from . import settings
from .constants import DONOR_URL, DONOR_CHECK_TIME, DONOR_TIMEOUT, COMMON_ADDON
from .util import get_kodi_string, set_kodi_string
from .log import log

KEY = '_slyguy_donor_{}'.format(COMMON_ADDON.getAddonInfo('version'))

def is_donor(force=False):

        return True

import uuid

from slyguy.settings import CommonSettings
from slyguy.settings.types import Bool, Enum, AutoText
from slyguy.constants import *
from slyguy import mem_cache

from .language import _


class State:
    AUTO = ''
    NSW = 'NSW'
    VIC = 'VIC'
    QLD = 'QLD'
    WA = 'WA'
    SA = 'SA'


class Settings(CommonSettings):
    STATE = Enum('state', _.STATE, default=State.AUTO, after_clear=mem_cache.empty, after_save= lambda _: mem_cache.empty(),
        options=[[_.AUTO, State.AUTO], [_.NSW, State.NSW], [_.VIC, State.VIC], [_.QLD, State.QLD], [_.WA, State.WA], [_.SA, State.SA]])
    FLATTEN_SINGLE_SEASON = Bool('flatten_single_season', _.FLATTEN_SEASONS, default=True)
    HIDE_EXTRAS = Bool('hide_extras', _.HIDE_EXTRAS, default=False)
    DEVICE_ID = AutoText('device_id', _.DEVICE_ID, generator=uuid.uuid4, confirm_clear=_.CLEAR_DEVICE_ID)


settings = Settings()

"""
Constants and configurations for Mitsui crawling
"""
from typing import Final

from app.core.config import settings

# URL and selector configurations
URL_MULTI: Final = 'https://www.mitsui-chintai.co.jp/rf/result?'  # Trang chứa các thẻ có phân trang của mitsui
ITEM_SELECTOR: Final = 'tr.c-room-list__body-row[data-js-room-link]'  # Thẻ phần tử
ITEM_MAX_NUM_PAGE: Final = 'li.c-pagination__item > a.c-pagination__link[href]'

# Database configuration
ID_MONGO = settings.ID_MONGO_MITSUI
COLLECTION_NAME = settings.COLLECTION_NAME_MITSUI
DEFAULT_NUM_PAGES = 74 #74

# Default amenities configuration
DEFAULT_AMENITIES = {
    "room_link": "mitsui_link",
    'credit_card': 'Y',
    'no_guarantor': 'Y', 
    'aircon': 'Y',
    'aircon_heater': 'Y',
    'bs': 'Y',
    'cable': 'Y',
    'internet_broadband': 'Y',
    'internet_wifi': 'Y',
    'phoneline': 'Y',
    'flooring': 'Y',
    'system_kitchen': 'Y',
    'bath': 'Y',
    'shower': 'Y',
    'unit_bath': 'Y',
    'western_toilet': 'Y',
    'fire_insurance': 20000,
}
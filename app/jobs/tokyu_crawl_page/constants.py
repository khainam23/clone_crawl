"""
Constants and configurations for Tokyu crawling
"""
from typing import Final

from app.core.config import settings

# Base URL configuration
BASE_URL: Final = 'https://rent.tokyu-housing-lease.co.jp'

# URL and selector configurations
URL_MULTI: Final = 'https://rent.tokyu-housing-lease.co.jp/rent_search/%E5%9F%BC%E7%8E%89%E7%9C%8C-%E5%8D%83%E8%91%89%E7%9C%8C-%E6%9D%B1%E4%BA%AC%E9%83%BD-%E7%A5%9E%E5%A5%88%E5%B7%9D%E7%9C%8C/limit:50/page:'  # Trang chứa các property có phân trang của tokyu
ITEM_SELECTOR: Final = 'table.check_table tbody td a'  # Thẻ phần tử chứa link
ITEM_MAX_NUM_PAGE: Final = 'li.pgnt > a[href]'  # Thẻ pagination để detect số trang tối đa
DEFAULT_NUM_PAGES = 30

# Database configuration
ID_MONGO = settings.ID_MONGO_TOKYU
COLLECTION_NAME = settings.COLLECTION_NAME_TOKYU

# Default amenities configuration
DEFAULT_AMENITIES = {
    "room_link": "tokyu_link",
    'credit_card': 'Y',
    'aircon': 'Y',
    'aircon_heater': 'Y',
    'bs': 'Y',
    'internet_broadband': 'Y',
    'phoneline': 'Y',
    'flooring': 'Y',
    'system_kitchen': 'Y',
    'bath': 'Y',
    'shower': 'Y',
    'unit_bath': 'Y',
    'western_toilet': 'Y',
}
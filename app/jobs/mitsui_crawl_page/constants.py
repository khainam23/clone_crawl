"""
Constants and configurations for Mitsui crawling
"""
from typing import Final

from app.core.config import settings

# URL and selector configurations
url_multi: Final = 'https://www.mitsui-chintai.co.jp/rf/result?'  # Trang chứa các thẻ có phân trang của mitsui
item_selector: Final = 'tr.c-room-list__body-row[data-js-room-link]'  # Thẻ phần tử

# Batch processing configuration
batch_size = settings.batch_size  # Số lượng trang được crawl trong mỗi lần chạy (lấy từ .env)

# Image processing configuration
IMAGE_SKIP_PATTERNS = ['icon', 'logo', 'button', 'arrow', 'common']  # Các thể loại ảnh sẽ bỏ qua
MAX_IMAGES = 16  # Số lượng ảnh tối đa

# Database configuration
ID_MONGO = 11000000
COLLECTION_NAME = "room_mitsui"

# Timeout configurations
GALLERY_TIMEOUT = 5

# Station API configuration
STATION_API_BASE_URL = "https://bmatehouse.com/api/routes/get_by_position"
MAX_STATIONS = 5

# Coordinate conversion constants
COORDINATE_OFFSET_LAT = -1.291213
COORDINATE_OFFSET_LON = -5.82497
DEFAULT_ZONE = 9

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

# Direction mapping
DIRECTION_MAPPING = {
    '北': 'facing_north',
    '北東': 'facing_northeast', 
    '東': 'facing_east',
    '東南': 'facing_southeast',
    '南': 'facing_south',
    '南西': 'facing_southwest',
    '西': 'facing_west',
    '西北': 'facing_northwest',
    '北西': 'facing_northwest'
}

# Amenities mapping
AMENITIES_MAPPING = {
    'フロント': 'concierge',
    '宅配ロッカー': 'delivery_box',
    'オートロック': 'autolock',
    'バイク置場': 'motorcycle_parking',
    '敷地内ごみ置場': 'cleaning_service',
    'エレベータ': 'elevator',
    '24時間管理': 'cleaning_service',
    '防犯カメラ': 'autolock',
    'セキュリティシステム': 'autolock',
    'バルコニー': 'balcony',
    'バストイレ': 'unit_bath',
    '洗面所独立': 'separate_toilet',
    '室内洗濯機置場': 'washing_machine',
    'バス有': 'bath',
    '浴室乾燥機': 'bath_water_heater',
    '給湯追い焚き有': 'auto_fill_bath',
    'キッチン有': 'system_kitchen',
    'コンロ有': 'range',
    'グリル': 'oven',
    'オープン': 'counter_kitchen',
    'インターネット': 'internet_broadband',
    'BS': 'bs',
    'CS': 'cable',
    'ピアノ可': 'furnished',
    'ウォークインクロゼット': 'storage',
    'ペット可': 'pets',
    'エアコン': 'aircon',
    'フローリング': 'flooring',
    'システムキッチン': 'system_kitchen',
    'シャワー': 'shower',
    'ガス': 'gas',
    'WiFi': 'internet_wifi',
    'Wi-Fi': 'internet_wifi',
    'インターホン': 'autolock',
    'TVモニター付インターホン': 'autolock',
    '宅配BOX': 'delivery_box',
    'ゴミ置場': 'cleaning_service',
    '温水洗浄便座': 'washlet',
    '床暖房': 'underfloor_heating',
    '食器洗い乾燥機': 'dishwasher',
    'IHクッキングヒーター': 'induction_cooker',
    '追い焚き機能': 'auto_fill_bath',
    '宅配ボックス': 'delivery_box',
    'オール電化': 'all_electric',
    'カウンターキッチン': 'counter_kitchen',
    'ロフト': 'loft',
    'ルーフバルコニー': 'roof_balcony',
    'ベランダ': 'veranda',
    '庭': 'yard',
    'SOHO可': 'soho',
    '女性限定': 'female_only',
    '学生可': 'student_friendly',
}

# Structure mapping
STRUCTURE_MAPPING = {
    "木造": "wood",
    "ブロック": "cb",
    "鉄骨造": "steel_frame",
    "鉄筋コンクリート（RC）": "rc",
    "鉄骨鉄筋コンクリート（SRC）": "src",
    "プレキャストコンクリート（PC）": "pc",
    "鉄骨プレキャスト（HPC）": "other",
    "軽量鉄骨": "light_gauge_steel",
    "軽量気泡コンクリート（ALC）": "alc",
    "その他": "other",
}
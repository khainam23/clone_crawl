"""
Constants and configurations for Tokyu crawling
"""
from typing import Final

from app.core.config import settings

# Base URL configuration
BASE_URL: Final = 'https://rent.tokyu-housing-lease.co.jp'

# URL and selector configurations
url_multi: Final = 'https://rent.tokyu-housing-lease.co.jp/rent_search/%E5%9F%BC%E7%8E%89%E7%9C%8C-%E5%8D%83%E8%91%89%E7%9C%8C-%E6%9D%B1%E4%BA%AC%E9%83%BD-%E7%A5%9E%E5%A5%88%E5%B7%9D%E7%9C%8C/limit:50/page:'  # Trang chứa các property có phân trang của tokyu
item_selector: Final = 'table.check_table tbody td a'  # Thẻ phần tử chứa link

# Batch processing configuration
batch_size = settings.batch_size  # Số lượng trang được crawl trong mỗi lần chạy (lấy từ .env)

# Database configuration
ID_MONGO = 12000000
COLLECTION_NAME = "tokyu_properties"

# Default amenities configuration
DEFAULT_AMENITIES = {
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

# Amenities mapping for Tokyu
AMENITIES_MAPPING = {
    # Building amenities
    '宅配BOX': 'delivery_box',
    '宅配ボックス': 'delivery_box',
    'メールボックス': 'delivery_box',
    'エレベーター': 'elevator',
    'TVモニター付インターホン': 'autolock',
    'オートロック': 'autolock',
    '自転車置場': 'bicycle_parking',
    'バイク置場': 'motorcycle_parking',
    '防犯カメラ': 'security_camera',
    'ごみ置場': 'cleaning_service',
    '24時間ゴミ出し可': 'cleaning_service',
    '管理人': 'concierge',
    'BS対応可': 'bs',
    'CS110°対応可': 'cable',
    'インターネット使用料不要': 'internet_broadband',
    'インターネット': 'internet_broadband',
    '電話回線': 'phoneline',
    '敷地内駐車場': 'parking',
    
    # Room amenities
    '壁掛けエアコン': 'aircon',
    'エアコン': 'aircon',
    'システムキッチン': 'system_kitchen',
    'グリル': 'oven',
    '温水洗浄便座': 'washlet',
    'シャワー付洗面台': 'shower',
    '浴室乾燥機能': 'bath_water_heater',
    '追焚機能': 'auto_fill_bath',
    '独立洗面化粧台': 'separate_toilet',
    'バストイレ別': 'separate_toilet',
    'ダブルロック': 'autolock',
    'ディンプルキー': 'autolock',
    '玄関人感照明センサー': 'autolock',
    'シューズボックス': 'storage',
    'ウォークインクローゼット': 'storage',
    'フローリング': 'flooring',
    'リビングダイニング照明付': 'furnished',
    '洋室照明付': 'furnished',
    '室内洗濯機置場': 'washing_machine',
    '24時間換気システム': 'ventilation',
    '防音サッシ': 'soundproof',
    'バルコニー': 'balcony',
    'ベランダ': 'veranda',
    'ロフト': 'loft',
    'ペット飼育可': 'pets',
    '床暖房': 'underfloor_heating',
    'IHクッキングヒーター': 'induction_cooker',
    '食器洗い乾燥機': 'dishwasher',
    'オール電化': 'all_electric',
    'カウンターキッチン': 'counter_kitchen',
    'ルーフバルコニー': 'roof_balcony',
    '庭': 'yard',
    'SOHO可': 'soho',
    '女性限定': 'female_only',
    '学生可': 'student_friendly',
}

# Timeout configurations
GALLERY_TIMEOUT = 10
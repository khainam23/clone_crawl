"""
Amenities processing utilities
"""
from typing import Dict, Any, List
import difflib

AMENITIES_MAPPING = {
    '宅配BOX': 'delivery_box',
    '宅配ボックス': 'delivery_box',
    'メールボックス': 'delivery_box',
    'エレベーター': 'elevator',
    'TVモニター付インターホン': 'autolock',
    'オートロック': 'autolock',
    '自転車置場': 'bicycle_parking',
    'バイク置場': 'motorcycle_parking',
    '防犯カメラ': 'autolock',
    'ごみ置場': 'cleaning_service',
    '24時間ゴミ出し可': 'cleaning_service',
    '管理人': 'concierge',
    'BS対応可': 'bs',
    'CS110°対応可': 'cable',
    'インターネット使用料不要': 'internet_broadband',
    'インターネット': 'internet_broadband',
    '電話回線': 'phoneline',
    '敷地内駐車場': 'parking',
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
    'フロント': 'concierge',
    '宅配ロッカー': 'delivery_box',
    '敷地内ごみ置場': 'cleaning_service',
    'エレベータ': 'elevator',
    '24時間管理': 'cleaning_service',
    'セキュリティシステム': 'autolock',
    'バストイレ': 'unit_bath',
    '洗面所独立': 'separate_toilet',
    'バス有': 'bath',
    '浴室乾燥機': 'bath_water_heater',
    '給湯追い焚き有': 'auto_fill_bath',
    'キッチン有': 'system_kitchen',
    'コンロ有': 'range',
    'オープン': 'counter_kitchen',
    'BS': 'bs',
    'CS': 'cable',
    'ピアノ可': 'furnished',
    'ウォークインクロゼット': 'storage',
    'ペット可': 'pets',
    'ガス': 'gas',
    'WiFi': 'internet_wifi',
    'Wi-Fi': 'internet_wifi',
    'インターホン': 'autolock',
}

def process_amenities_text(amenities_text: str) -> List[Dict[str, str]]:
    """
    Process amenities text and map Japanese amenities to field names
    using diff-based similarity matching
    
    Args:
        amenities_text: Raw amenities text from HTML
        
    Returns:
        List of dictionaries with amenity info
    """
    found_amenities = []
    
    # Split the amenities text into individual items
    amenity_items = [item.strip() for item in amenities_text.split(',')]
    
    for jp_amenity, field_name in AMENITIES_MAPPING.items():
        # Check for exact match first (for efficiency)
        if jp_amenity in amenities_text:
            found_amenities.append({
                'japanese': jp_amenity,
                'field': field_name
            })
            continue
            
        # If no exact match, check for similarity with each item
        for item in amenity_items:
            similarity = difflib.SequenceMatcher(None, jp_amenity, item).ratio()
            if similarity >= 0.5:
                found_amenities.append({
                    'japanese': jp_amenity,
                    'field': field_name,
                })
                break
    
    return found_amenities


def apply_amenities_to_data(amenities_text: str, data: Dict[str, Any]) -> None:
    """
    Apply found amenities to data dictionary
    
    Args:
        data: Data dictionary to update
        found_amenities: List of found amenities
    """
    found_amenities = process_amenities_text(amenities_text)
    for amenity in found_amenities:
        data[amenity['field']] = 'Y'
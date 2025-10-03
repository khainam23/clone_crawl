"""
Location utilities for extracting district information from coordinates
Shared utility for both Mitsui and Tokyu crawlers
"""
from typing import Dict, Any
from app.utils import city_utils, district_utils, prefecture_utils


def get_district_info(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Get district information from coordinates stored in data
    
    Args:
        data: Dictionary containing 'map_lat' and 'map_lng' keys
        
    Returns:
        Updated data dictionary with district, prefecture, and city information
    """
    map_lat = data.get('map_lat')
    map_lng = data.get('map_lng')
    
    if not map_lat or not map_lng:
        return data
    
    try:
        # Convert to float for district lookup
        lat = float(map_lat)
        lng = float(map_lng)
        
        district_name, prefecture_id, city_id = district_utils.get_district(lat, lng)
        
        data['district'] = district_name
        
        prefecture_name = prefecture_utils.get_prefecture_by_id(prefecture_id)
        city_name = city_utils.get_city_by_id(city_id)
        
        data['prefecture'] = prefecture_name
        data['city'] = city_name
        
    except (ValueError, TypeError) as e:
        print(f"❌ Error converting coordinates for district lookup: {e}")
    except Exception as e:
        print(f"❌ Error getting district information: {e}")
        
    return data
from typing import Dict, Any

from app.utils.coordinate_utils import fetch_coordinates_from_google_maps
from app.utils.location_utils import get_district_info

class MapExtractor:
    def __init__(self):
        pass
        
    def extract_map(self, data: Dict[str, Any], html: str) -> Dict[str, Any]:
        """
        Extract map coordinates using Google Maps API based on address
        Similar to Mitsui implementation
        """
        address = data.get('address')
        
        if not address:
            print("⚠️ No address provided for coordinate fetching")
            return data
        
        try:
            print(f"🌐 Fetching coordinates from Google Maps for: {address}")
            result = fetch_coordinates_from_google_maps(address)
            
            if result:
                lat, lng = result
                data.update({
                    'map_lat': lat,
                    'map_lng': lng
                })
                print(f"✅ Coordinates found: Lat={lat:.6f}, Lng={lng:.6f}")
                
                # Get district information using shared utility
                get_district_info(data)
            else:
                print(f"⚠️ No coordinates found for address: {address}")
                
        except Exception as e:
            print(f"❌ Error fetching coordinates: {e}")
            
        return data
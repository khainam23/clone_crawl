"""
Station service for fetching nearby stations
"""
import requests
from typing import Dict, Any, List

from app.utils.http_client_utils import http_client
from app.core.config import settings


class StationService:
    """Handles station API requests and processing"""
    
    def get_nearby_stations(self, lat: str, lng: str) -> List[Dict[str, str]]:
        """Get nearby stations from API"""
        if not lat or not lng:
            print("❌ Missing coordinates for station lookup")
            return []
        
        try:
            # Construct API URL using constant
            api_url = f"{settings.STATION_URL}?lng={lng}&lat={lat}"
            print(f"🚉 Fetching stations: {api_url}")
            
            # Use the existing session for consistency
            response = http_client.get(api_url, timeout=settings.GALLERY_TIMEOUT)
            
            if response.status_code != 200:
                print(f"❌ Station API failed: HTTP {response.status_code}")
                return []
            
            stations_data = response.json()
            
            if not isinstance(stations_data, list):
                print("❌ Invalid station API response format")
                return []
            
            # Process stations using MAX_STATIONS constant
            stations_list = []
            for station_info in stations_data[:settings.MAX_STATIONS]:  # Limit using constant
                station_name = station_info.get('name')
                lines_info = station_info.get('lines_info', [])
                walk_time = round(float(station_info.get('distance', 0)) * 12.5)
                
                if not station_name or not lines_info:
                    continue
                
                # Get first line name
                train_line_name = lines_info[0].get('name') if lines_info else None
                
                if train_line_name:
                    stations_list.append({
                        'station_name': station_name,
                        'train_line_name': train_line_name,
                        'walk_time': walk_time
                    })
            
            if stations_list:
                print(f"🚉 Found {len(stations_list)} stations")
            else:
                print("⚠️ No valid stations found")
            
            return stations_list
                
        except requests.exceptions.Timeout:
            print("⏰ Station API request timeout")
        except Exception as e:
            print(f"❌ Station API error: {e}")
        
        return []
    
    def set_station_data(self, data: Dict[str, Any], html: str) -> Dict[str, Any]:
        """Get nearby stations from API and save to data"""
        map_lat = data.get('map_lat')
        map_lng = data.get('map_lng')
        
        stations = self.get_nearby_stations(map_lat, map_lng)
        if stations:
            data['stations'] = stations
        
        return data
    
    
Station_Service = StationService()
from typing import Dict, Any

from app.utils.html_processor_utils import htmlProcessor
from app.utils.http_client_utils import http_client
from app.jobs.tokyu_crawl_page.constants import BASE_URL
from app.utils.location_utils import get_district_info
from app.core.config import settings

class MapExtractor:
    def __init__(self):
        self.html_processor = htmlProcessor
        
    def extract_map(self, data: Dict[str, Any], html: str) -> Dict[str, Any]:
        """
        Extract map coordinates from div#gmap_road and get district information
        First tries to find coordinates in current HTML, if not found, accesses the access page
        """
        try:

            print("Trying redirect page to access page for map extraction...")
            access_html = self._fetch_access_page(html)
            
            if access_html:
                lat_value = self.html_processor.find(r'<div[^>]*id="gmap_road"[^>]*data-lat="([^"]*)"', access_html)
                lng_value = self.html_processor.find(r'<div[^>]*id="gmap_road"[^>]*data-lng="([^"]*)"', access_html)
            
            if not lat_value or not lng_value:
                print("⚠️ Could not find lat/lng data attributes in div#gmap_road")
                return data
            
            try:
                # Convert to float to validate
                lat = float(lat_value)
                lng = float(lng_value)
                
                # Store coordinates as strings (consistent with mitsui implementation)
                data.update({
                    'map_lat': float(lat),
                    'map_lng': float(lng)
                })
                
                print(f"🗺️ Extracted coordinates: Lat={lat:.6f}, Lng={lng:.6f}")
                
                # Get district information using shared utility
                get_district_info(data)
                
            except (ValueError, TypeError) as e:
                print(f"❌ Invalid coordinate values: lat={lat_value}, lng={lng_value}, error={e}")
                
        except Exception as e:
            print(f"❌ Error extracting map coordinates: {e}")
            
        return data
    
    def _fetch_access_page(self, html: str) -> str:
        """
        Fetch the access page from li.fl.access > a link
        """
        try:
            # Find access link from li.fl.access > a
            access_link_path = self.html_processor.find(
                r'<li[^>]*class="[^"]*fl[^"]*access[^"]*"[^>]*>.*?<a[^>]*href="([^"]+)"', 
                html
            )
            
            if not access_link_path:
                print("⚠️ No access link found in li.fl.access")
                return None
                
            access_link = BASE_URL + access_link_path
            print(f"🔗 Found access link: {access_link}")
            
            print(f"🗺️ Fetching access page: {access_link}")
            response = http_client.get(access_link, timeout=settings.GALLERY_TIMEOUT)
            
            if response.status_code != 200:
                print(f"❌ Access page fetch failed: HTTP {response.status_code}")
                return None
                
            print("✅ Successfully fetched access page")
            return response.text
            
        except Exception as e:
            print(f"❌ Error fetching access page: {e}")
            return None
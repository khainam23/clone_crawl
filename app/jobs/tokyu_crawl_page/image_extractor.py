"""
Image extraction utilities for Tokyu crawling
"""
from typing import Dict, Any

from app.utils.html_processor_utils import htmlProcessor
from app.utils.http_client_utils import http_client
from app.jobs.tokyu_crawl_page.constants import BASE_URL
from app.core.config import settings


class ImageExtractor:
    """Handles image extraction from gallery"""
    
    def __init__(self):
        self.html_processor = htmlProcessor
    
    def extract_images(self, data: Dict[str, Any], html: str) -> Dict[str, Any]:
        """Extract and organize images from HTML"""
        images_list = []
        
        try:
            # Tìm link gallery từ li.print_album>a
            gallery_link_path = self.html_processor.find(
                r'<li[^>]*class="[^"]*print_album[^"]*"[^>]*>.*?<a[^>]*href="([^"]+)"', 
                html
            )
            
            if not gallery_link_path:
                print("⚠️ No gallery link found")
                return data
                
            gallery_link = BASE_URL + gallery_link_path
            print(f"🔗 Found gallery link: {gallery_link}")
            
            print(f"🖼️ Fetching gallery: {gallery_link}")
            response = http_client.get(gallery_link, timeout=settings.GALLERY_TIMEOUT)
            
            if response.status_code != 200:
                print(f"❌ Gallery fetch failed: HTTP {response.status_code}")
                return data
                
            gallery_html = response.text
            
            # Extract exterior (div#mansion_img_album>*>ul>li:first>img)
            exterior_img = self.html_processor.find(
                r'<div[^>]*id="mansion_img_album"[^>]*>.*?<ul[^>]*>.*?<li[^>]*>.*?<img[^>]*src="([^"]+)"', 
                gallery_html
            )
            if exterior_img:
                images_list.append({'url': BASE_URL + exterior_img, 'category': 'exterior'})
                
            # Extract floorplan (div#room_photo_album >*>ul.clearFix>li:first>img)
            floorplan_img = self.html_processor.find(
                r'<div[^>]*id="room_photo_album"[^>]*>.*?<ul[^>]*class="[^"]*clearFix[^"]*"[^>]*>.*?<li[^>]*>.*?<img[^>]*src="([^"]+)"', 
                gallery_html
            )
            if floorplan_img:
                images_list.append({'url': BASE_URL + floorplan_img, 'category': 'floorplan'})
            
            # Extract interior images (div#common_area_album>*>ul>li>img)
            interior_pattern = self.html_processor.compile_regex(
                r'<div[^>]*id="common_area_album"[^>]*>.*?<ul[^>]*>(.*?)</ul>'
            )
            interior_section = interior_pattern.search(gallery_html)
            
            if interior_section:
                img_pattern = self.html_processor.compile_regex(r'<img[^>]*src="([^"]+)"')
                interior_imgs = img_pattern.findall(interior_section.group(1))
                
                for img_url in interior_imgs:
                    images_list.append({'url': BASE_URL + img_url, 'category': 'interior'})
            
        except Exception as e:
            print(f"❌ Image extraction error: {e}")
        
        if images_list:
            data['images'] = images_list
            
        return data
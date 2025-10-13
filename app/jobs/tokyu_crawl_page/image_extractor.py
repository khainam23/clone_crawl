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
        """Extract and organize images from HTML - optimized version"""
        images_list = []
        max_images = settings.MAX_IMAGES
        used_filenames = set()
        
        try:
            # Tìm link gallery từ li.print_album>a
            gallery_link_path = self.html_processor.find(
                r'<li[^>]*class="[^"]*print_album[^"]*"[^>]*>.*?<a[^>]*href="([^"]+)"', 
                html
            )
            
            if not gallery_link_path:
                return data
                
            gallery_link = BASE_URL + gallery_link_path
            
            # Optimized: reduced timeout, no verbose logging
            response = http_client.get(
                gallery_link, 
                timeout=(3, 7)  # (connect timeout, read timeout)
            )
            
            if response.status_code != 200:
                return data
                
            gallery_html = response.text
            
            # Extract exterior (div#mansion_img_album>*>ul>li:first>img)
            exterior_img = self.html_processor.find(
                r'<div[^>]*id="mansion_img_album"[^>]*>.*?<ul[^>]*>.*?<li[^>]*>.*?<img[^>]*src="([^"]+)"', 
                gallery_html
            )
            if exterior_img:
                filename = exterior_img.split('/')[-1]
                if filename not in used_filenames:
                    images_list.append({'url': BASE_URL + exterior_img, 'category': 'exterior'})
                    used_filenames.add(filename)
                
            # Extract floorplan (div#room_photo_album >*>ul.clearFix>li:first>img)
            if len(images_list) < max_images:
                floorplan_img = self.html_processor.find(
                    r'<div[^>]*id="room_photo_album"[^>]*>.*?<ul[^>]*class="[^"]*clearFix[^"]*"[^>]*>.*?<li[^>]*>.*?<img[^>]*src="([^"]+)"', 
                    gallery_html
                )
                if floorplan_img:
                    filename = floorplan_img.split('/')[-1]
                    if filename not in used_filenames:
                        images_list.append({'url': BASE_URL + floorplan_img, 'category': 'floorplan'})
                        used_filenames.add(filename)
            
            # Extract interior images (div#common_area_album>*>ul>li>img)
            remaining_slots = max_images - len(images_list)
            if remaining_slots > 0:
                interior_pattern = self.html_processor.compile_regex(
                    r'<div[^>]*id="common_area_album"[^>]*>.*?<ul[^>]*>(.*?)</ul>'
                )
                interior_section = interior_pattern.search(gallery_html)
                
                if interior_section:
                    img_pattern = self.html_processor.compile_regex(r'<img[^>]*src="([^"]+)"')
                    interior_imgs = img_pattern.findall(interior_section.group(1))
                    
                    # Optimized: limit iterations and check duplicates
                    for img_url in interior_imgs[:remaining_slots]:
                        filename = img_url.split('/')[-1]
                        if filename not in used_filenames:
                            images_list.append({'url': BASE_URL + img_url, 'category': 'interior'})
                            used_filenames.add(filename)
                            if len(images_list) >= max_images:
                                break
            
        except Exception:
            pass  # Silent fail for batch processing
        
        if images_list:
            data['images'] = images_list
            
        return data
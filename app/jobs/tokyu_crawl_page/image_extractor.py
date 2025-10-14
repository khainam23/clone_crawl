"""
Image extraction utilities for Tokyu crawling
"""
import re
from typing import Dict, Any

from app.utils.html_processor_utils import htmlProcessor
from app.jobs.tokyu_crawl_page.constants import BASE_URL
from app.core.config import settings


class ImageExtractor:
    """Handles image extraction from gallery"""
    
    def __init__(self):
        self.html_processor = htmlProcessor
    
    def extract_images(self, data: Dict[str, Any], html: str) -> Dict[str, Any]:
        """Extract and organize images from HTML - all images are on the main page"""
        images_list = []
        max_images = settings.MAX_IMAGES
        used_filenames = set()
        
        try:
            # Extract floorplan from #side_roomplan > p > a > img
            floorplan_pattern = self.html_processor.compile_regex(
                r'<[^>]*id="side_roomplan"[^>]*>(.*?)</(?:div|section|aside)',
                re.DOTALL
            )
            floorplan_section = floorplan_pattern.search(html)
            
            if floorplan_section:
                floorplan_content = floorplan_section.group(1)
                floorplan_img = self.html_processor.find(
                    r'<img[^>]*src="([^"]+)"',
                    floorplan_content
                )
                if floorplan_img:
                    filename = floorplan_img.split('/')[-1]
                    if filename not in used_filenames:
                        full_url = floorplan_img if floorplan_img.startswith('http') else BASE_URL + floorplan_img
                        images_list.append({'url': full_url, 'category': 'floorplan'})
                        used_filenames.add(filename)
            
            # Extract album_photos section - find content between album_photos and gmap_view
            album_pattern = self.html_processor.compile_regex(
                r'<div[^>]*id="album_photos"[^>]*>(.*?)<div[^>]*id="gmap_view"',
                re.DOTALL
            )
            album_section = album_pattern.search(html)
            
            if album_section:
                album_content = album_section.group(1)
                
                # Extract exterior from div#m000
                exterior_img = self.html_processor.find(
                    r'<div[^>]*id="m000"[^>]*>.*?<img[^>]*src="([^"]+)"',
                    album_content
                )
                if exterior_img and len(images_list) < max_images:
                    filename = exterior_img.split('/')[-1]
                    if filename not in used_filenames:
                        full_url = exterior_img if exterior_img.startswith('http') else BASE_URL + exterior_img
                        images_list.append({'url': full_url, 'category': 'exterior'})
                        used_filenames.add(filename)
                
                # Extract interior images from div#i00x (i001, i002, i003, etc.)
                remaining_slots = max_images - len(images_list)
                if remaining_slots > 0:
                    # Find all divs with id matching i00x pattern
                    interior_divs_pattern = self.html_processor.compile_regex(
                        r'<div[^>]*id="i\d{3}"[^>]*>.*?<img[^>]*src="([^"]+)"',
                        re.DOTALL
                    )
                    interior_imgs = interior_divs_pattern.findall(album_content)
                    
                    for img_url in interior_imgs[:remaining_slots]:
                        filename = img_url.split('/')[-1]
                        if filename not in used_filenames:
                            full_url = img_url if img_url.startswith('http') else BASE_URL + img_url
                            images_list.append({'url': full_url, 'category': 'interior'})
                            used_filenames.add(filename)
                            if len(images_list) >= max_images:
                                break
            
        except Exception as e:
            pass  # Silent fail for batch processing
        
        if images_list:
            data['images'] = images_list
            
        return data
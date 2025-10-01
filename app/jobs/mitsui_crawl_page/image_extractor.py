"""
Image extraction utilities for Mitsui crawling
"""
import requests
from typing import Dict, Any, Tuple, List

from app.utils.html_processor_utils import HtmlProcessor
from app.utils.http_client_utils import http_client
from app.core.config import settings


class ImageExtractor:
    """Handles image extraction from gallery"""
    
    def __init__(self):
        self.html_processor = HtmlProcessor()
    
    def get_gallery_images(self, html: str) -> Tuple[List[str], List[str], List[str]]:
        """Extract gallery images with optimized request handling"""
        floorplan_images = []
        exterior_images = []
        interior_images = []
        
        # 1. Floor plan
        firstfloor_url = self.html_processor.find(r'RF_firstfloorplan_photo\s*=\s*["\']([^"\']+)["\']', html)
        if firstfloor_url and firstfloor_url != "null":
            floorplan_images.append(firstfloor_url)

        # 2. Gallery
        gallery_url = self.html_processor.find(r'RF_gallery_url\s*=\s*["\']([^"\']+)["\']', html)
        if not gallery_url or gallery_url == "null":
            return exterior_images, floorplan_images, interior_images
        
        try:
            print(f"🖼️ Fetching gallery: {gallery_url}")
            response = http_client.get(gallery_url, timeout=settings.GALLERY_TIMEOUT)
            
            if response.status_code != 200:
                print(f"❌ Gallery fetch failed: HTTP {response.status_code}")
                return exterior_images, floorplan_images, interior_images
            
            gallery_data = response.json()
            for item in gallery_data:
                filename = item.get("filename", "")
                if not filename:
                    continue
                    
                room_no = item.get("ROOM_NO", 0)
                if room_no == 99999 and not exterior_images:
                    exterior_images.append(filename)
                else:
                    interior_images.append(filename)
                    
        except requests.exceptions.Timeout:
            print("⏰ Gallery request timeout")
        except Exception as e:
            print(f"❌ Gallery request error: {e}")
        
        return exterior_images, floorplan_images, interior_images
    
    def extract_images(self, data: Dict[str, Any], html: str) -> Dict[str, Any]:
        """Extract and organize images from HTML"""
        images_list = []
        used_urls = set()
        used_names = set()

        def add_image(img_url: str, category: str) -> bool:
            """Add image if not duplicate and under limit"""
            if (len(images_list) >= settings.MAX_IMAGES or 
                img_url in used_urls or 
                img_url.split('/')[-1] in used_names):
                return False

            images_list.append({'url': img_url, 'category': category})
            used_urls.add(img_url)
            used_names.add(img_url.split('/')[-1])
            return True

        try:
            exterior_images, floorplan_images, interior_images = self.get_gallery_images(html)

            # Exterior → lấy đúng 1 ảnh
            if exterior_images:
                add_image(exterior_images[0], "exterior")

            # Floorplan → lấy đúng 1 ảnh
            if floorplan_images:
                add_image(floorplan_images[0], "floorplan")

            # Interior → lấy nhiều cho đến khi đủ MAX_IMAGES
            for img_url in interior_images:
                add_image(img_url, "interior")

        except Exception as e:
            print(f"❌ Image extraction error: {e}")

        if images_list:
            data['images'] = images_list

        return data
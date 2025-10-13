"""
Image extraction utilities for Mitsui crawling
"""
import requests, gc
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
            max_needed = settings.MAX_IMAGES + 1
            for item in gallery_data[:max_needed]:
                filename = item.get("filename", "")
                if not filename:
                    continue
                    
                room_no = item.get("ROOM_NO", 0)
                if room_no == 99999 and not exterior_images:
                    exterior_images.append(filename)
                else:
                    interior_images.append(filename)
            
            gallery_data = None
            response = None
            gc.collect()
                    
        except requests.exceptions.Timeout:
            print("⏰ Gallery request timeout")
        except Exception as e:
            print(f"❌ Gallery request error: {e}")
        
        return exterior_images, floorplan_images, interior_images
    
    def extract_images(self, data: Dict[str, Any], html: str) -> Dict[str, Any]:
        """Extract and organize images from HTML - optimized version"""
        images_list = []
        used_names = set()  # Only track filenames, not full URLs
        max_images = settings.MAX_IMAGES

        try:
            exterior_images, floorplan_images, interior_images = self.get_gallery_images(html)

            # Exterior → exactly 1 image
            if exterior_images:
                filename = exterior_images[0].split('/')[-1]
                if filename not in used_names:
                    images_list.append({'url': exterior_images[0], 'category': 'exterior'})
                    used_names.add(filename)

            # Floorplan → exactly 1 image
            if floorplan_images and len(images_list) < max_images:
                filename = floorplan_images[0].split('/')[-1]
                if filename not in used_names:
                    images_list.append({'url': floorplan_images[0], 'category': 'floorplan'})
                    used_names.add(filename)

            # Interior → fill up to MAX_IMAGES
            remaining_slots = max_images - len(images_list)
            if remaining_slots > 0:
                for img_url in interior_images[:remaining_slots]:  # Slice to avoid unnecessary iterations
                    filename = img_url.split('/')[-1]
                    if filename not in used_names:
                        images_list.append({'url': img_url, 'category': 'interior'})
                        used_names.add(filename)
                        if len(images_list) >= max_images:
                            break

            # Giải phóng bộ nhớ
            exterior_images = None
            floorplan_images = None
            interior_images = None
            used_names = None
            gc.collect()
        except Exception:
            pass  # Silent fail for batch processing

        if images_list:
            data['images'] = images_list

        return data
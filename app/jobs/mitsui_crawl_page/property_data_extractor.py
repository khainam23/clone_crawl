"""Property data extraction utilities for Mitsui crawling"""
import re
import sys
import asyncio
import calendar
from typing import Dict, Any, Optional, Tuple
from datetime import datetime, date
from concurrent.futures import ThreadPoolExecutor

from app.utils.html_processor_utils import HtmlProcessor
from app.utils.direction_utils import extract_direction_info
from app.utils.structure_utils import extract_structure_info as utils_extract_structure_info
from app.utils.amenities_utils import apply_amenities_to_data
from app.utils.property_utils import PropertyUtils
from app.utils.coordinate_utils import fetch_coordinates_from_google_maps
from app.services.station_service import Station_Service
from app.jobs.mitsui_crawl_page.coordinate_converter import CoordinateConverter
from app.jobs.mitsui_crawl_page.constants import DEFAULT_AMENITIES
from app.utils.location_utils import get_district_info
from app.utils.room_type_utils import extract_room_type
from app.utils.translate_utils import translate_ja_to_en

class PropertyDataExtractor:
    """Handles extraction of property data from HTML"""
    
    # Tạo thread pool với 1 worker để tránh tràn RAM khi chạy nhiều Chrome instances
    # Chrome headless tốn ~150-300MB RAM mỗi instance
    EXECUTOR = ThreadPoolExecutor(max_workers=1)
    
    def __init__(self):
        self.html_processor = HtmlProcessor()
        self.coordinate_converter = CoordinateConverter()
        self.station_service = Station_Service
        self._dt_dd_cache = None
    
    def _parse_html_once(self, html: str) -> None:
        """Parse HTML once and cache all dt/dd pairs"""
        if self._dt_dd_cache is None:
            self._dt_dd_cache = self.html_processor.parse_all_dt_dd(html)
    
    def _get_dt_dd(self, dt_label: str) -> Optional[str]:
        """Get cached dt/dd content"""
        if self._dt_dd_cache is None:
            return None
        content = self._dt_dd_cache.get(dt_label)
        return self.html_processor.clean_html(content) if content else None
    
    async def _parse_coordinates(self, address: str, data: Dict[str, Any]) -> None:
        """Fetch coordinates from Google Maps and update data directly"""
        if not address:
            print("⚠️ No address provided for coordinate fetching")
            return

        try:
            print(f"🌐 Fetching coordinates from Google Maps for: {address}")
            
            # Run sync Selenium in thread pool to avoid event loop issues
            loop = asyncio.get_event_loop()
            
            result = await loop.run_in_executor(
                self.EXECUTOR, 
                fetch_coordinates_from_google_maps, 
                address
            )
            
            if result:
                lat, lng = result
                data.update({
                    'map_lat': lat,
                    'map_lng': lng
                })
                print(f"✅ Coordinates found: Lat={lat:.6f}, Lng={lng:.6f}")
            else:
                print(f"⚠️ No coordinates found for address: {address}")

        except Exception as e:
            print(f"❌ Error in coordinate fetching: {e}")
    
    def _extract_dt_dd_content(self, html: str, dt_label: str) -> Optional[str]:
        """Extract content from dt/dd pattern"""
        cached = self._get_dt_dd(dt_label)
        return cached if cached is not None else self.html_processor.extract_dt_dd_content(html, dt_label)
    
    def _safe_extract(self, func_name: str, func, data: Dict[str, Any], html: str):
        """Safe extraction with error handling"""
        try:
            func(data, html)
        except Exception as e:
            print(f"❌ Error in {func_name}: {e}")
            
            
    #==========================# Methods #========================#
    def get_static_info(self, data: Dict[str, Any], html: str) -> Dict[str, Any]:
        """Process static information extraction"""
        self._parse_html_once(html)
        
        extractors = [
            ('header_info', self.extract_header_info),
            ('available_from', self.extract_available_from),
            ('parking', self.extract_parking),
            ('address_info', self.extract_address_info),
            ('rent_info', self.extract_rent_info),
            ('estimated_rent', self.extract_estimated_rent),
            ('room_info', self.extract_room_info),
            ('construction_date', self.extract_construction_date),
            ('structure_info', self.extract_structure_info),
            ('renewal_fee', self.extract_renewal_fee),
            ('direction_info', self.extract_direction_info),
            ('lock_exchange', self.extract_lock_exchange),
            ('amenities', self.extract_amenities),
            ('building_description', self.extract_building_description),
        ]
        
        for name, extractor in extractors:
            self._safe_extract(name, extractor, data, html)
        
        return data
    
    async def convert_coordinates(self, data: Dict[str, Any], html: str) -> Dict[str, Any]:
        """Fetch coordinates from Google Maps using address from data"""
        # Get address from data (already extracted by extract_address_info)
        address = data.get('address')
        
        # Fetch coordinates and update data directly
        if address:
            await self._parse_coordinates(address, data)
        
        return data
    
    def set_default_amenities(self, data: Dict[str, Any], html: str) -> Dict[str, Any]:
        return PropertyUtils.set_default_amenities(data, DEFAULT_AMENITIES)
    
    def process_pricing(self, data: Dict[str, Any], html: str) -> Dict[str, Any]:
        return PropertyUtils.process_pricing(data)
    
    def cleanup_temp_fields(self, data: Dict[str, Any], html: str) -> Dict[str, Any]:
        self._dt_dd_cache = None
        return PropertyUtils.cleanup_temp_fields(data, '_html')
    
    def extract_header_info(self, data: Dict[str, Any], html: str):
        """Extract building name, floor, and room number"""
        h1_content = self.html_processor.find(r'<h1[^>]*>(.*?)</h1>', html)
        if not h1_content:
            return
        
        h1_text = self.html_processor.clean_html(h1_content)
        match = re.match(r'^(.+?)\s+(\d+)階(\d+)$', h1_text)
        
        if match:
            data.update({
                'building_name_ja': match.group(1).strip(),
                'floor_no': int(match.group(2)) if match.group(2) else 1,
                'unit_no': int(match.group(3))
            })
        else:
            data['building_name_ja'] = h1_text
            
        data['building_name_en'] = translate_ja_to_en(text = data['building_name_ja'])

    def extract_available_from(self, data: Dict[str, Any], html: str):
        """Extract available from date"""
        text = self._extract_dt_dd_content(html, '入居可能日')
        if not text:
            return

        current_year = datetime.now().year
        parsed_date = None

        if "即可" in text:
            parsed_date = date.today()
        else:
            for key, day in {"上旬": "5日", "中旬": "15日", "下旬": "25日"}.items():
                text = re.sub(rf'(\d{{4}}年)?(\d{{1,2}})月{key}', 
                            lambda m: f"{m.group(1) or str(current_year)+'年'}{m.group(2)}月{day}", text)

            if m := re.search(r'(\d{4})?年?(\d{1,2})月末', text):
                year = int(m.group(1)) if m.group(1) else current_year
                month = int(m.group(2))
                last_day = calendar.monthrange(year, month)[1]
                text = f"{year}年{month}月{last_day}日"

            patterns = [
                (r'(\d{4})年(\d{1,2})月(\d{1,2})日', lambda y,m,d: date(int(y), int(m), int(d))),
                (r'(\d{1,2})月(\d{1,2})日', lambda m,d: date(current_year, int(m), int(d))),
                (r'(\d{4})/(\d{1,2})/(\d{1,2})', lambda y,m,d: date(int(y), int(m), int(d))),
                (r'(\d{1,2})/(\d{1,2})', lambda m,d: date(current_year, int(m), int(d))),
            ]

            for pat, conv in patterns:
                if m := re.search(pat, text):
                    parsed_date = conv(*m.groups())
                    break

        if parsed_date:
            data["available_from"] = parsed_date.isoformat()

    def extract_parking(self, data: Dict[str, Any], html: str):
        """Extract parking availability"""
        parking_text = self._extract_dt_dd_content(html, '駐車場')
        if not parking_text:
            data['parking'] = 'Y'
            return
        
        negative_values = ['なし', '無し', '×', '不可', 'ー', '無', 'NO', 'No', 'no']
        data['parking'] = 'N' if any(neg in parking_text for neg in negative_values) else 'Y'
    
    def extract_address_info(self, data: Dict[str, Any], html: str):
        """Extract address information"""
        address_section = self.html_processor.find(r'<dt[^>]*>所在地</dt>(.*?)(?=<dt|</dl>|$)', html)
        if not address_section:
            return
        
        dd_matches = re.findall(r'<dd[^>]*>(.*?)</dd>', address_section, re.DOTALL)
        
        if len(dd_matches) >= 2:
            address_text = self.html_processor.clean_html(dd_matches[1])
            address_parts = self.coordinate_converter.parse_japanese_address(address_text)
            
            data['address'] = address_text
            if address_parts.get('chome_banchi'):
                data['chome_banchi'] = address_parts['chome_banchi']
            
    
    def extract_rent_info(self, data: Dict[str, Any], html: str):
        """Extract rent and maintenance fee"""
        rent_match = re.search(r'<dd[^>]*class="[^"]*__rent[^"]*"[^>]*>(.*?)</dd>', html, re.DOTALL)
        if not rent_match:
            return
        
        rent_text = self.html_processor.clean_html(rent_match.group(1))
        rent_text = re.sub(r"\s+", " ", rent_text.replace("／", "/").replace(",", "").strip())

        monthly_rent = monthly_maintenance = 0

        if match := re.search(r'(\d+)円\s*/\s*(\d+)円', rent_text):
            monthly_rent, monthly_maintenance = int(match.group(1)), int(match.group(2))
        elif match := re.search(r'(\d+)円.*管理費\s*(\d+)円', rent_text):
            monthly_rent, monthly_maintenance = int(match.group(1)), int(match.group(2))
        elif match := re.search(r'(\d+)円', rent_text):
            monthly_rent = int(match.group(1))
            
        agency_fee = int(monthly_rent * 1.1)

        data.update({'monthly_rent': monthly_rent, 'monthly_maintenance': monthly_maintenance, 'numeric_agency': agency_fee})

    def extract_deposit_key_info(self, data: Dict[str, Any], html: str) -> Dict[str, Any]:
        """Extract deposit and key money"""
        deposit_key_text = self._extract_dt_dd_content(html, '敷金／礼金')
        total_monthly = data.get('total_monthly', 0)
        
        if deposit_key_text and total_monthly:
             if match := re.search(r'([\d.]+)ヶ月\s*/\s*([\d.]+)ヶ月', deposit_key_text):
                data.update({
                    'numeric_deposit': float(match.group(1)) * total_monthly,
                    'numeric_key': float(match.group(2)) * total_monthly
                })
        
        data['total_monthly'] = None
        return data
                
    def extract_room_info(self, data: Dict[str, Any], html: str):
        """Extract room type and size"""
        room_info_text = self._extract_dt_dd_content(html, '間取り・面積')
        if room_info_text and (match := re.search(r'^([^/]+?)\s*/\s*([\d.]+)㎡', room_info_text)):
            data.update({
                'room_type': extract_room_type(match.group(1).strip()),
                'size': float(match.group(2))
            })
    
    def extract_construction_date(self, data: Dict[str, Any], html: str):
        """Extract construction date"""
        construction_text = self._extract_dt_dd_content(html, '竣工日')
        if construction_text and (match := re.search(r'(\d{4})年', construction_text)):
            data['year'] = int(match.group(1))
    
    def extract_structure_info(self, data: Dict[str, Any], html: str):
        """Extract building structure"""
        structure_text = self._extract_dt_dd_content(html, '規模構造')
        if structure_text and (match := re.search(r'^(.*?造)\s*地上(\d+)階(?:地下(\d+)階建?)?', structure_text)):
            data.update({
                'structure': utils_extract_structure_info(match.group(1).strip()),
                'floors': int(match.group(2))
            })
            if match.group(3):
                data['basement_floors'] = int(match.group(3))
    
    def extract_renewal_fee(self, data: Dict[str, Any], html: str):
        """Extract renewal fee"""
        renewal_text = self._extract_dt_dd_content(html, '更新料')
        if renewal_text and (match := re.search(r'新賃料の(\d+)ヶ月分', renewal_text)):
            months = int(match.group(1))
            data.update({
                'renewal_new_rent': 'Y',
                'months_renewal': 12 if months == 1 else months
            })
    
    def extract_direction_info(self, data: Dict[str, Any], html: str):
        """Extract apartment facing direction"""
        if direction_text := self._extract_dt_dd_content(html, '方位'):
            print(f"🧭 Direction: {direction_text}")
            extract_direction_info(data, direction_text)
    
    def extract_estimated_rent(self, data: Dict[str, Any], html: str):
        """Extract めやす賃料 (estimated rent) as total_monthly"""
        if estimated_rent_text := self._extract_dt_dd_content(html, 'めやす賃料'):
            if match := re.search(r'([\d,]+)円', estimated_rent_text):
                data['total_monthly'] = int(match.group(1).replace(',', ''))
            else:
                data['total_monthly'] = 0
    
    def extract_lock_exchange(self, data: Dict[str, Any], html: str):
        """Extract lock exchange fee"""
        if other_fees_text := self._extract_dt_dd_content(html, 'その他費用'):
            data['property_other_expenses_ja'] = other_fees_text
            if match := re.search(r'玄関錠交換代[^\d]*([\d,]+)円', other_fees_text):
                data['lock_exchange'] = int(match.group(1).replace(',', ''))
    
    def extract_amenities(self, data: Dict[str, Any], html: str):
        """Extract amenities"""
        if amenities_text := self._extract_dt_dd_content(html, '専有部・共用部設備'):
            apply_amenities_to_data(amenities_text, data)
    
    def extract_building_description(self, data: Dict[str, Any], html: str):
        """Extract building description"""
        if description_text := self._extract_dt_dd_content(html, '備考'):
            data['building_description_ja'] = description_text
    
    #=========================# Other methods #======================#
    
    def extract_station(self, data: Dict[str, Any], html: str):
        self.station_service.set_station_data(data=data, html=html)
        return data
    
    def get_info_district(self, data: Dict[str, Any], html: str) -> Dict[str, Any]:
        return get_district_info(data)
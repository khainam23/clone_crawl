"""
Property data extraction utilities for Mitsui crawling
Optimized version with grouped extraction methods
"""
import re
import calendar
from typing import Dict, Any, Optional, Tuple
from datetime import datetime, date

from app.utils.html_processor_utils import HtmlProcessor
from app.utils.direction_utils import extract_direction_info
from app.utils.structure_utils import extract_structure_info as utils_extract_structure_info
from app.utils.amenities_utils import apply_amenities_to_data
from app.utils.property_utils import PropertyUtils
from app.services.station_service import Station_Service
from app.jobs.mitsui_crawl_page.coordinate_converter import CoordinateConverter
from app.jobs.mitsui_crawl_page.constants import DEFAULT_AMENITIES
from app.utils.location_utils import get_district_info


class PropertyDataExtractor:
    """Handles extraction of property data from HTML with optimized methods"""
    
    def __init__(self):
        self.html_processor = HtmlProcessor()
        self.coordinate_converter = CoordinateConverter()
        self.station_service = Station_Service
    
    # ==================== HELPER METHODS ====================
    
    def _extract_dt_dd_content(self, html: str, dt_label: str) -> Optional[str]:
        """Helper: Extract content from <dt>label</dt><dd>content</dd> pattern"""
        return self.html_processor.extract_dt_dd_content(html, dt_label)
    
    def _safe_extract(self, func_name: str, func, data: Dict[str, Any], html: str):
        """Helper: Safe extraction with error handling"""
        try:
            func(data, html)
        except Exception as e:
            print(f"❌ Error in {func_name}: {e}")
    
    def convert_coordinates(self, data: Dict[str, Any], html: str) -> Dict[str, Any]:
        """Convert coordinates from XY to lat/lon"""
        try:
            x_value = self.html_processor.find(r'name="[^"]*MAP_X"[^>]*value="([^"]*)"', html)
            y_value = self.html_processor.find(r'name="[^"]*MAP_Y"[^>]*value="([^"]*)"', html)
            
            if x_value and y_value:
                x, y = float(x_value), float(y_value)
                lat, lon = self.coordinate_converter.xy_to_latlon_tokyo(x, y)
                
                data.update({
                    'map_lat': str(lat),
                    'map_lng': str(lon)
                })
                
                print(f"🗺️ Coordinates: X={x}, Y={y} → Lat={lat:.6f}, Lng={lon:.6f}")
                
        except Exception as e:
            print(f"❌ Coordinate conversion error: {e}")
        
        return data
    
    def set_default_amenities(self, data: Dict[str, Any], html: str) -> Dict[str, Any]:
        """Set default amenities using global constants"""
        return PropertyUtils.set_default_amenities(data, DEFAULT_AMENITIES)
    
    def process_pricing(self, data: Dict[str, Any], html: str) -> Dict[str, Any]:
        """Process pricing calculations with validation"""
        return PropertyUtils.process_pricing(data)
    
    def cleanup_temp_fields(self, data: Dict[str, Any], html: str) -> Dict[str, Any]:
        """Remove temporary fields that shouldn't be in final JSON"""
        return PropertyUtils.cleanup_temp_fields(data, '_html')
    
    # ==================== EXTRACTION METHODS ====================
    
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
                'floor_no': int(match.group(2)),
                'unit_no': int(match.group(3))
            })
        else:
            data['building_name_ja'] = h1_text

    def extract_available_from(self, data: Dict[str, Any], html: str):
        """Extract available from date with Japanese date format support"""
        text = self._extract_dt_dd_content(html, '入居可能日')
        if not text:
            return

        current_year = datetime.now().year
        parsed_date = None

        if "即可" in text:
            parsed_date = date.today()
        else:
            # Normalize 上旬/中旬/下旬
            for key, day in {"上旬": "5日", "中旬": "15日", "下旬": "25日"}.items():
                text = re.sub(rf'(\d{{4}}年)?(\d{{1,2}})月{key}', 
                            lambda m: f"{m.group(1) or str(current_year)+'年'}{m.group(2)}月{day}", text)

            # Handle 月末
            m = re.search(r'(\d{4})?年?(\d{1,2})月末', text)
            if m:
                year = int(m.group(1)) if m.group(1) else current_year
                month = int(m.group(2))
                last_day = calendar.monthrange(year, month)[1]
                text = f"{year}年{month}月{last_day}日"

            # Parse date patterns
            patterns = [
                (r'(\d{4})年(\d{1,2})月(\d{1,2})日', lambda y,m,d: date(int(y), int(m), int(d))),
                (r'(\d{1,2})月(\d{1,2})日', lambda m,d: date(current_year, int(m), int(d))),
                (r'(\d{4})/(\d{1,2})/(\d{1,2})', lambda y,m,d: date(int(y), int(m), int(d))),
                (r'(\d{1,2})/(\d{1,2})', lambda m,d: date(current_year, int(m), int(d))),
            ]

            for pat, conv in patterns:
                m = re.search(pat, text)
                if m:
                    parsed_date = conv(*m.groups())
                    break

        if parsed_date:
            data["available_from"] = parsed_date.isoformat()
            print(f"📅 Parsed available_from: {parsed_date}")

    def extract_parking(self, data: Dict[str, Any], html: str):
        """Extract parking availability (default Y if not negative)"""
        parking_text = self._extract_dt_dd_content(html, '駐車場')
        if not parking_text:
            data['parking'] = 'Y'
            return
        
        # Negative values in Japanese
        negative_values = ['なし', '無し', '×', '不可', 'ー', '無', 'NO', 'No', 'no']
        is_negative = any(neg_val in parking_text for neg_val in negative_values)
        
        data['parking'] = 'N' if is_negative else 'Y'
        print(f"🚗 Parking: {data['parking']} ({parking_text})")
    
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
            
            print(f"🏠 Address: {address_text}")
    
    def extract_rent_info(self, data: Dict[str, Any], html: str):
        """Extract rent and maintenance fee from HTML"""
        rent_match = re.search(r'<dd[^>]*class="[^"]*__rent[^"]*"[^>]*>(.*?)</dd>', html, re.DOTALL)
        if not rent_match:
            return
        
        rent_text = self.html_processor.clean_html(rent_match.group(1))
        rent_text = rent_text.replace("／", "/").replace(",", "").strip()
        rent_text = re.sub(r"\s+", " ", rent_text)

        monthly_rent = 0
        monthly_maintenance = 0

        # Try different patterns
        if match := re.search(r'(\d+)円\s*/\s*(\d+)円', rent_text):
            monthly_rent = int(match.group(1))
            monthly_maintenance = int(match.group(2))
        elif match := re.search(r'(\d+)円.*管理費\s*(\d+)円', rent_text):
            monthly_rent = int(match.group(1))
            monthly_maintenance = int(match.group(2))
        elif match := re.search(r'(\d+)円', rent_text):
            monthly_rent = int(match.group(1))

        data.update({
            'monthly_rent': monthly_rent,
            'monthly_maintenance': monthly_maintenance
        })

        print(f"💰 Rent: {monthly_rent}円, Maintenance: {monthly_maintenance}円")
    
    def extract_deposit_key_info(self, data: Dict[str, Any], html: str) -> Dict[str, Any]:
        """Extract deposit and key money information"""
        deposit_key_text = self._extract_dt_dd_content(html, '敷金／礼金')
        if not deposit_key_text:
            return data
        
        total_monthly = data.get('total_monthly', 0)
        if not total_monthly:
            return data
        
        if match := re.search(r'([\d.]+)ヶ月\s*/\s*([\d.]+)ヶ月', deposit_key_text):
            data.update({
                'numeric_deposit': float(match.group(1)) * total_monthly,
                'numeric_key': float(match.group(2)) * total_monthly
            })
            print(f"💰 Deposit/Key: {deposit_key_text}")
            
        # Remove temporary field
        data['total_monthly'] = None
            
        return data
                
    def extract_room_info(self, data: Dict[str, Any], html: str):
        """Extract room type and size"""
        room_info_text = self._extract_dt_dd_content(html, '間取り・面積')
        if not room_info_text:
            return
        
        if match := re.search(r'^([^/]+?)\s*/\s*([\d.]+)㎡', room_info_text):
            room_type = re.sub(r'[^\w]', '', match.group(1).strip())
            data.update({
                'room_type': room_type,
                'size': float(match.group(2))
            })
            print(f"🏠 Room: {room_type}, Size: {match.group(2)}㎡")
    
    def extract_construction_date(self, data: Dict[str, Any], html: str):
        """Extract construction date"""
        construction_text = self._extract_dt_dd_content(html, '竣工日')
        if not construction_text:
            return
        
        if match := re.search(r'(\d{4})年', construction_text):
            data['year'] = int(match.group(1))
            print(f"📅 Construction year: {match.group(1)}")
    
    def extract_structure_info(self, data: Dict[str, Any], html: str):
        """Extract building structure information with mapping"""
        structure_text = self._extract_dt_dd_content(html, '規模構造')
        if not structure_text:
            return
        
        if match := re.search(r'^(.*?造)\s*地上(\d+)階(?:地下(\d+)階建?)?', structure_text):
            original_structure = match.group(1).strip()
            
            # Use the utility function from structure_utils.py
            mapped_structure = utils_extract_structure_info(original_structure)
            
            data.update({
                'structure': mapped_structure,
                'floors': int(match.group(2))
            })
            
            if match.group(3):
                data['basement_floors'] = int(match.group(3))
                
            print(f"🏗️ Structure: {original_structure} → {mapped_structure}")

    
    def extract_renewal_fee(self, data: Dict[str, Any], html: str):
        """Extract renewal fee information"""
        renewal_text = self._extract_dt_dd_content(html, '更新料')
        if not renewal_text:
            return
        
        if match := re.search(r'新賃料の(\d+)ヶ月分', renewal_text):
            months = int(match.group(1))
            data.update({
                'renewal_new_rent': 'Y',
                'months_renewal': 12 if months == 1 else months
            })
            print(f"🔄 Renewal: {months} months")
    
    def extract_direction_info(self, data: Dict[str, Any], html: str):
        """Extract apartment facing direction"""
        direction_text = self._extract_dt_dd_content(html, '方位')
        if direction_text:
            extract_direction_info(direction_text)
    
    def extract_lock_exchange(self, data: Dict[str, Any], html: str):
        """Extract lock exchange fee"""
        other_fees_text = self._extract_dt_dd_content(html, 'その他費用')
        if not other_fees_text:
            return
        
        data['property_other_expenses_ja'] = other_fees_text
        
        if match := re.search(r'玄関錠交換代[^\d]*([\d,]+)円', other_fees_text):
            data['lock_exchange'] = int(match.group(1).replace(',', ''))
            print(f"🔑 Lock exchange: {match.group(1)}円")
    
    def extract_amenities(self, data: Dict[str, Any], html: str):
        """Extract amenities information"""
        amenities_text = self._extract_dt_dd_content(html, '専有部・共用部設備')
        if amenities_text:
            apply_amenities_to_data(amenities_text, data)
    
    def extract_building_description(self, data: Dict[str, Any], html: str):
        """Extract building description"""
        description_text = self._extract_dt_dd_content(html, '備考')
        if description_text:
            data['building_description_ja'] = description_text
            print(f"📝 Description: {description_text[:50]}...")
    
    def get_static_info(self, data: Dict[str, Any], html: str) -> Dict[str, Any]:
        """Process static information extraction using modular approach with safe extraction"""
        # List of extraction methods to run
        extractors = [
            ('header_info', self.extract_header_info),
            ('available_from', self.extract_available_from),
            ('parking', self.extract_parking),
            ('address_info', self.extract_address_info),
            ('rent_info', self.extract_rent_info),
            ('room_info', self.extract_room_info),
            ('construction_date', self.extract_construction_date),
            ('structure_info', self.extract_structure_info),
            ('renewal_fee', self.extract_renewal_fee),
            ('direction_info', self.extract_direction_info),
            ('lock_exchange', self.extract_lock_exchange),
            ('amenities', self.extract_amenities),
            ('building_description', self.extract_building_description),
        ]
        
        # Run all extractors with error handling
        for name, extractor in extractors:
            self._safe_extract(name, extractor, data, html)
        
        return data
    
    # ==================== EXTRACTION METHODS FOR LATER USE ====================
    
    def extract_station(self, data: Dict[str, Any], html: str):
        self.station_service.set_station_data(data = data, html = html)
        
        print(f"🚉 Station info extracted. {data['stations'][0].get('station_name')} ...")
        return data
    
    def get_info_district(self, data: Dict[str, Any], html: str) -> Dict[str, Any]:
        """Get district information from coordinates using shared utility"""
        return get_district_info(data)
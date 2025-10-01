"""
Property data extraction utilities for Mitsui crawling
"""
import re
import calendar
from typing import Dict, Any
from datetime import datetime, date

from app.utils.html_processor_utils import HtmlProcessor
from app.utils.direction_utils import extract_direction_info
from app.utils.structure_utils import extract_structure_info as utils_extract_structure_info
from app.utils.amenities_utils import apply_amenities_to_data
from app.jobs.mitsui_crawl_page.coordinate_converter import CoordinateConverter
from app.jobs.mitsui_crawl_page.constants import DEFAULT_AMENITIES
from app.utils.location_utils import get_district_info


class PropertyDataExtractor:
    """Handles extraction of property data from HTML"""
    
    def __init__(self):
        self.html_processor = HtmlProcessor()
        self.coordinate_converter = CoordinateConverter()
    
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
        data.update(DEFAULT_AMENITIES)
        return data
    
    def process_pricing(self, data: Dict[str, Any], html: str) -> Dict[str, Any]:
        """Process pricing calculations with validation"""
        if not all(key in data for key in ['monthly_rent', 'monthly_maintenance']):
            return data

        try:
            monthly_rent = data['monthly_rent']
            monthly_maintenance = data['monthly_maintenance']
            total_monthly = monthly_rent + monthly_maintenance

            if total_monthly > 0:
                data.update({
                    "total_monthly": total_monthly,
                    "numeric_guarantor": total_monthly * 50 // 100,
                    "numeric_guarantor_max": total_monthly * 80 // 100,
                })
                
                print(f"💰 Calculated pricing: total={total_monthly}円")
            else:
                print(f"⚠️ Invalid total monthly amount: {total_monthly}")

        except Exception as e:
            print(f"❌ Error processing pricing: {e}")

        return data
    
    def cleanup_temp_fields(self, data: Dict[str, Any], html: str) -> Dict[str, Any]:
        """Remove temporary fields that shouldn't be in final JSON"""
        if '_html' in data:
            del data['_html']
            print("🧹 Cleaned up temporary _html field")
        return data
    
    def extract_header_info(self, data: Dict[str, Any], html: str):
        """Extract building name, floor, and room number"""
        try:
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
                
        except Exception as e:
            print(f"❌ Error extracting header info: {e}")

    def extract_available_from(self, data: Dict[str, Any], html: str):
        """Extract available from date with Japanese date format support"""
        try:
            content = self.html_processor.find(r'<dt[^>]*>入居可能日</dt>\s*<dd[^>]*>(.*?)</dd>', html)
            if not content:
                return

            text = self.html_processor.clean_html(content)
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

        except Exception as e:
            print(f"❌ Error extracting available_from: {e}")

    def extract_parking(self, data: Dict[str, Any], html: str):
        """Extract parking availability (default Y if not negative)"""
        try:
            parking_content = self.html_processor.find(r'<dt[^>]*>駐車場</dt>\s*<dd[^>]*>(.*?)</dd>', html)
            if not parking_content:
                return
            
            parking_text = self.html_processor.clean_html(parking_content)
            
            # Negative values in Japanese
            negative_values = ['なし', '無し', '×', '不可', 'ー', '無', 'NO', 'No', 'no']
            is_negative = any(neg_val in parking_text for neg_val in negative_values)
            
            data['parking'] = 'N' if is_negative else 'Y'
            print(f"🚗 Parking: {data['parking']} ({parking_text})")
                
        except Exception as e:
            print(f"❌ Error extracting parking: {e}")
            data['parking'] = 'Y'
    
    def extract_address_info(self, data: Dict[str, Any], html: str):
        """Extract address information"""
        try:
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
                
        except Exception as e:
            print(f"❌ Error extracting address info: {e}")
    
    def extract_rent_info(self, data: Dict[str, Any], html: str):
        """Extract rent and maintenance fee from HTML"""
        try:
            rent_match = re.search(r'<dd[^>]*class="[^"]*__rent[^"]*"[^>]*>(.*?)</dd>', html, re.DOTALL)
            if not rent_match:
                return
            
            rent_text = self.html_processor.clean_html(rent_match.group(1))
            rent_text = rent_text.replace("／", "/").replace(",", "")
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

        except Exception as e:
            print(f"❌ Error extracting rent info: {e}")
    
    def extract_deposit_key_info(self, data: Dict[str, Any], html: str) -> Dict[str, Any]:
        """Extract deposit and key money information"""
        try:
            deposit_key_content = self.html_processor.find(r'<dt[^>]*>敷金／礼金</dt>\s*<dd[^>]*>(.*?)</dd>', html)
            if not deposit_key_content:
                return data
            
            total_monthly = data.get('total_monthly', 0)
            if not total_monthly:
                return data
            
            deposit_key_text = self.html_processor.clean_html(deposit_key_content)
            
            if match := re.search(r'([\d.]+)ヶ月\s*/\s*([\d.]+)ヶ月', deposit_key_text):
                data.update({
                    'numeric_deposit': float(match.group(1)) * total_monthly,
                    'numeric_key': float(match.group(2)) * total_monthly
                })
                print(f"💰 Deposit/Key: {deposit_key_text}")
                
            # Remove temporary field
            data['total_monthly'] = None
                
        except Exception as e:
            print(f"❌ Error extracting deposit/key info: {e}")
            
        return data
                
    def extract_room_info(self, data: Dict[str, Any], html: str):
        """Extract room type and size"""
        try:
            room_info_content = self.html_processor.find(r'<dt[^>]*>間取り・面積</dt>\s*<dd[^>]*>(.*?)</dd>', html)
            if not room_info_content:
                return
            
            room_info_text = self.html_processor.clean_html(room_info_content)
            
            if match := re.search(r'^([^/]+?)\s*/\s*([\d.]+)㎡', room_info_text):
                room_type = re.sub(r'[^\w]', '', match.group(1).strip())
                data.update({
                    'room_type': room_type,
                    'size': float(match.group(2))
                })
                print(f"🏠 Room: {room_type}, Size: {match.group(2)}㎡")
                
        except Exception as e:
            print(f"❌ Error extracting room info: {e}")
    
    def extract_construction_date(self, data: Dict[str, Any], html: str):
        """Extract construction date"""
        try:
            construction_content = self.html_processor.find(r'<dt[^>]*>竣工日</dt>\s*<dd[^>]*>(.*?)</dd>', html)
            if not construction_content:
                return
            
            construction_text = self.html_processor.clean_html(construction_content)
            
            if match := re.search(r'(\d{4})年', construction_text):
                data['year'] = int(match.group(1))
                print(f"📅 Construction year: {match.group(1)}")
                
        except Exception as e:
            print(f"❌ Error extracting construction date: {e}")
    
    def extract_structure_info(self, data: Dict[str, Any], html: str):
        """Extract building structure information with mapping"""
        try:
            structure_content = self.html_processor.find(r'<dt[^>]*>規模構造</dt>\s*<dd[^>]*>(.*?)</dd>', html)
            if not structure_content:
                return
            
            structure_text = self.html_processor.clean_html(structure_content)
            
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
                
        except Exception as e:
            print(f"❌ Error extracting structure info: {e}")

    
    def extract_renewal_fee(self, data: Dict[str, Any], html: str):
        """Extract renewal fee information"""
        try:
            renewal_content = self.html_processor.find(r'<dt[^>]*>更新料</dt>\s*<dd[^>]*>(.*?)</dd>', html)
            if not renewal_content:
                return
            
            renewal_text = self.html_processor.clean_html(renewal_content)
            
            if match := re.search(r'新賃料の(\d+)ヶ月分', renewal_text):
                months = int(match.group(1))
                data.update({
                    'renewal_new_rent': 'Y',
                    'months_renewal': 12 if months == 1 else months
                })
                print(f"🔄 Renewal: {months} months")
                
        except Exception as e:
            print(f"❌ Error extracting renewal fee: {e}")
    
    def extract_direction_info(self, data: Dict[str, Any], html: str):
        """Extract apartment facing direction"""
        try:
            direction_content = self.html_processor.find(r'<dt[^>]*>方位</dt>\s*<dd[^>]*>(.*?)</dd>', html)
            if not direction_content:
                return
            
            direction_text = self.html_processor.clean_html(direction_content)
            
            extract_direction_info(direction_text)
            
        except Exception as e:
            print(f"❌ Error extracting direction info: {e}")
    
    def extract_lock_exchange(self, data: Dict[str, Any], html: str):
        """Extract lock exchange fee"""
        try:
            other_fees_content = self.html_processor.find(r'<dt[^>]*>その他費用</dt>\s*<dd[^>]*>(.*?)</dd>', html)
            if not other_fees_content:
                return
            
            other_fees_text = self.html_processor.clean_html(other_fees_content)
            data['property_other_expenses_ja'] = other_fees_text
            
            if match := re.search(r'玄関錠交換代[^\d]*([\d,]+)円', other_fees_text):
                data['lock_exchange'] = int(match.group(1).replace(',', ''))
                print(f"🔑 Lock exchange: {match.group(1)}円")
                
        except Exception as e:
            print(f"❌ Error extracting lock exchange: {e}")
    
    def extract_amenities(self, data: Dict[str, Any], html: str):
        """Extract amenities information"""
        try:
            amenities_match = re.search(r'<dt[^>]*>専有部・共用部設備</dt>\s*<dd[^>]*>(.*?)</dd>', html, re.DOTALL)
            if not amenities_match:
                return
            
            amenities_text = self.html_processor.clean_html(amenities_match.group(1))
            
            apply_amenities_to_data(amenities_text, data)
                
        except Exception as e:
            print(f"❌ Error extracting amenities: {e}")
    
    def extract_building_description(self, data: Dict[str, Any], html: str):
        """Extract building description"""
        try:
            if match := re.search(r'<dt[^>]*>備考</dt>\s*<dd[^>]*>(.*?)</dd>', html, re.DOTALL):
                description_text = self.html_processor.clean_html(match.group(1))
                if description_text:
                    data['building_description_ja'] = description_text
                    print(f"📝 Description: {description_text[:50]}...")
                    
        except Exception as e:
            print(f"❌ Error extracting building description: {e}")
    
    def get_static_info(self, data: Dict[str, Any], html: str) -> Dict[str, Any]:
        """Process static information extraction using modular approach"""
        # Process each section using dedicated functions
        self.extract_header_info(data, html)
        self.extract_available_from(data, html)
        self.extract_parking(data, html)
        self.extract_address_info(data, html)
        self.extract_rent_info(data, html)
        self.extract_room_info(data, html)
        self.extract_construction_date(data, html)
        self.extract_structure_info(data, html)
        self.extract_renewal_fee(data, html)
        self.extract_direction_info(data, html)
        self.extract_lock_exchange(data, html)
        self.extract_amenities(data, html)
        self.extract_building_description(data, html)
        
        return data
    
    def get_info_district(self, data: Dict[str, Any], html: str) -> Dict[str, Any]:
        """Get district information from coordinates using shared utility"""
        return get_district_info(data)
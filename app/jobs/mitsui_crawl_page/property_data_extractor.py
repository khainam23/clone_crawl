"""
Property data extraction utilities for Mitsui crawling
"""
import re
import calendar
import difflib
from typing import Dict, Any
from datetime import datetime, date

from app.utils.html_processor_utils import HtmlProcessor
from app.jobs.mitsui_crawl_page.coordinate_converter import CoordinateConverter
from app.jobs.mitsui_crawl_page.constants import (
    DEFAULT_AMENITIES, DIRECTION_MAPPING, AMENITIES_MAPPING, 
    STRUCTURE_MAPPING
)
from app.utils import city_utils, district_utils, prefecture_utils
from app.utils.location_utils import get_district_info


class PropertyDataExtractor:
    """Handles extraction of property data from HTML"""
    
    def __init__(self):
        self.html_processor = HtmlProcessor()
        self.coordinate_converter = CoordinateConverter()
    
    def convert_coordinates(self, data: Dict[str, Any], html: str) -> Dict[str, Any]:
        """Convert coordinates from XY to lat/lon"""
        x_value = self.html_processor.find(r'name="[^"]*MAP_X"[^>]*value="([^"]*)"', html)
        y_value = self.html_processor.find(r'name="[^"]*MAP_Y"[^>]*value="([^"]*)"', html)
        
        if x_value and y_value:
            try:
                x, y = float(x_value), float(y_value)
                lat, lon = self.coordinate_converter.xy_to_latlon_tokyo(x, y)
                
                data.update({
                    'map_lat': str(lat),
                    'map_lng': str(lon)
                })
                
                print(f"🗺️ Converted: X={x}, Y={y} → Lat={lat:.6f}, Lng={lon:.6f}")
                
            except (ValueError, Exception) as e:
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
                print("⚠️ No h1 tag found")
                return
            
            h1_text = self.html_processor.clean_html(h1_content)
            pattern = self.html_processor.compile_regex(r'^(.+?)\s+(\d+)階(\d+)$')
            match = pattern.match(h1_text)
            
            if match:
                data.update({
                    'building_name_ja': match.group(1).strip(),
                    'floor_no': int(match.group(2)),
                    'unit_no': int(match.group(3))
                })
            else:
               data.update({
                    'building_name_ja': h1_text,
                })
                
        except Exception as e:
            print(f"❌ Error extracting header info: {e}")

    def extract_available_from(self, data: Dict[str, Any], html: str):
        """
        Trích 入居可能日, chuyển đổi thành date object.
        - '即可' -> hôm nay
        - '上旬' -> ngày 5
        - '中旬' -> ngày 15
        - '下旬' -> ngày 25
        - '月末' -> ngày cuối tháng
        """
        try:
            content = self.html_processor.find(r'<dt[^>]*>入居可能日</dt>\s*<dd[^>]*>(.*?)</dd>', html)
            text = self.html_processor.clean_html(content) if content else ""
            if not text:
                return

            current_year = datetime.now().year
            parsed_date = None

            if "即可" in text:
                parsed_date = date.today()
                print(f"📅 Available immediately: {parsed_date}")
            else:
                # 上旬/中旬/下旬 → ngày cố định
                for key, day in {"上旬": "5日", "中旬": "15日", "下旬": "25日"}.items():
                    text = re.sub(rf'(\d{{4}}年)?(\d{{1,2}})月{key}', 
                                lambda m: f"{m.group(1) or str(current_year)+'年'}{m.group(2)}月{day}", 
                                text)

                # 月末 → ngày cuối tháng
                m = re.search(r'(\d{4})?年?(\d{1,2})月末', text)
                if m:
                    year = int(m.group(1)) if m.group(1) else current_year
                    month = int(m.group(2))
                    last_day = calendar.monthrange(year, month)[1]
                    text = f"{year}年{month}月{last_day}日"

                # regex patterns
                patterns = [
                    (r'(\d{4})年(\d{1,2})月(\d{1,2})日', lambda y,m,d: date(int(y), int(m), int(d))),
                    (r'(\d{1,2})月(\d{1,2})日',          lambda m,d: date(current_year, int(m), int(d))),
                    (r'(\d{4})/(\d{1,2})/(\d{1,2})',   lambda y,m,d: date(int(y), int(m), int(d))),
                    (r'(\d{1,2})/(\d{1,2})',           lambda m,d: date(current_year, int(m), int(d))),
                ]

                for pat, conv in patterns:
                    m = re.search(pat, text)
                    if m:
                        parsed_date = conv(*m.groups())
                        break

            data["available_from"] = parsed_date.isoformat()
            if parsed_date:
                print(f"📅 Parsed available_from: {parsed_date} (from: {text})")
            else:
                print(f"⚠️ Could not parse date from: {text}")

        except Exception as e:
            print(f"❌ Error extracting available_from: {e}")
            data["available_from"] = None

    def extract_parking(self, data: Dict[str, Any], html: str):
        '''
        Xử lý tại 駐車場 lấy dd liền kề
        Nó sẽ là kiểu Yes No tiếng nhật nhưng đôi lúc sẽ có trường hợp đặc biệt, xử lý bằng cách nếu không rơi vào phủ định thì đánh cho parking là Y
        '''
        try:
            # Tìm thẻ dt chứa "駐車場" và thẻ dd ngay sau nó
            parking_content = self.html_processor.find(r'<dt[^>]*>駐車場</dt>\s*<dd[^>]*>(.*?)</dd>', html)
            if not parking_content:
                print("⚠️ No parking section found")
                return
            
            # Làm sạch HTML và lấy text
            parking_text = self.html_processor.clean_html(parking_content).strip()
            if not parking_text:
                print("⚠️ Parking content is empty after cleaning")
                return
            
            print(f"🚗 Found parking text: {parking_text}")
            
            # Danh sách các giá trị phủ định tiếng Nhật
            negative_values = [
                'なし',     # nashi - không có
                '無し',     # nashi - không có (kanji)
                '×',        # dấu X
                '不可',     # fuka - không được phép
                'ー',       # dấu gạch ngang
                '無',       # mu - không có
                'NO',       # tiếng Anh
                'No',       # tiếng Anh
                'no',       # tiếng Anh
            ]
            
            # Kiểm tra xem có phải giá trị phủ định không
            is_negative = any(neg_val in parking_text for neg_val in negative_values)
            
            if is_negative:
                data['parking'] = 'N'
                print(f"🚗 Set parking to N (negative value found): {parking_text}")
            else:
                data['parking'] = 'Y'
                print(f"🚗 Set parking to Y (positive or neutral value): {parking_text}")
                
        except Exception as e:
            print(f"❌ Error extracting parking: {e}")
            # Trong trường hợp lỗi, mặc định là Y theo yêu cầu
            data['parking'] = 'Y'
            print("🚗 Set parking to Y (default due to error)")
    
    def extract_address_info(self, data: Dict[str, Any], html: str):
        """Extract address information"""
        try:
            address_section = self.html_processor.find(r'<dt[^>]*>所在地</dt>(.*?)(?=<dt|</dl>|$)', html)
            if not address_section:
                print("⚠️ No address section found")
                return
            
            dd_pattern = self.html_processor.compile_regex(r'<dd[^>]*>(.*?)</dd>')
            dd_matches = dd_pattern.findall(address_section)
            
            if len(dd_matches) >= 2:
                address_text = self.html_processor.clean_html(dd_matches[1])
                address_parts = self.coordinate_converter.parse_japanese_address(address_text)
                
                data['address'] = address_text
                if address_parts['chome_banchi']:
                    data['chome_banchi'] = address_parts['chome_banchi']
                
                print(f"🏠 Set address: {address_text}")
            else:
                print(f"⚠️ Found {len(dd_matches)} dd tags, expected at least 2")
                
        except Exception as e:
            print(f"❌ Error extracting address info: {e}")
    
    def extract_rent_info(self, data: Dict[str, Any], html: str):
        """Extract rent and maintenance fee from HTML"""
        try:
            # Match toàn bộ <dd class="__rent">...</dd>
            rent_pattern = self.html_processor.compile_regex(r'<dd[^>]*class="[^"]*__rent[^"]*"[^>]*>(.*?)</dd>')
            rent_match = rent_pattern.search(html)
            
            if not rent_match:
                print("⚠️ No rent class found")
                return
            
            rent_text = self.html_processor.clean_html(rent_match.group(1))
            print(f"🏠 Found rent text: {rent_text}")

            # Normalize
            rent_text = rent_text.replace("／", "/")
            rent_text = rent_text.replace(",", "")
            rent_text = re.sub(r"\s+", " ", rent_text)

            # Case 1: rent / maintenance
            match1 = re.search(r'(\d+)円\s*/\s*(\d+)円', rent_text)
            # Case 2: rent 管理費 maintenance
            match2 = re.search(r'(\d+)円.*管理費\s*(\d+)円', rent_text)
            # Case 3: only rent
            match3 = re.search(r'(\d+)円', rent_text)

            monthly_rent = 0
            monthly_maintenance = 0

            if match1:
                monthly_rent = int(match1.group(1))
                monthly_maintenance = int(match1.group(2))
            elif match2:
                monthly_rent = int(match2.group(1))
                monthly_maintenance = int(match2.group(2))
            elif match3:
                monthly_rent = int(match3.group(1))
                monthly_maintenance = 0
            else:
                print(f"⚠️ Rent format not matched: {rent_text}")
                return

            data.update({
                'monthly_rent': monthly_rent,
                'monthly_maintenance': monthly_maintenance
            })

            print(f"💰 Extracted rent: {monthly_rent}円, maintenance: {monthly_maintenance}円")

        except Exception as e:
            print(f"❌ Error extracting rent info: {e}")
    
    def extract_deposit_key_info(self, data: Dict[str, Any], html: str):
        """Extract deposit and key money information"""
        deposit_key_content = self.html_processor.find(r'<dt[^>]*>敷金／礼金</dt>\s*<dd[^>]*>(.*?)</dd>', html)
        if not deposit_key_content:
            print("⚠️ No deposit/key section found")
            return
        
        total_monthly = data['total_monthly']
        
        deposit_key_text = self.html_processor.clean_html(deposit_key_content)
        print(f"💰 Found deposit/key info: {deposit_key_text}")
        
        pattern = self.html_processor.compile_regex(r'([\d.]+)ヶ月\s*/\s*([\d.]+)ヶ月')
        match = pattern.search(deposit_key_text)
        
        if match:
            data.update({
                'numeric_deposit': float(match.group(1)) * total_monthly,
                'numeric_key': float(match.group(2)) * total_monthly
            })
            
        # Xóa key vì không dùng nữa
        data['total_monthly'] = None
            
        return data
                
    def extract_room_info(self, data: Dict[str, Any], html: str):
        """Extract room type and size"""
        try:
            room_info_content = self.html_processor.find(r'<dt[^>]*>間取り・面積</dt>\s*<dd[^>]*>(.*?)</dd>', html)
            if not room_info_content:
                print("⚠️ No room info section found")
                return
            
            room_info_text = self.html_processor.clean_html(room_info_content)
            pattern = self.html_processor.compile_regex(r'^([^/]+?)\s*/\s*([\d.]+)㎡')
            match = pattern.search(room_info_text)
            
            if match:
                room_type = re.sub(r'[^\w]', '', match.group(1).strip())
                size = float(match.group(2))
                
                data.update({
                    'room_type': room_type,
                    'size': size
                })
                
        except Exception as e:
            print(f"❌ Error extracting room info: {e}")
    
    def extract_construction_date(self, data: Dict[str, Any], html: str):
        """Extract construction date"""
        try:
            construction_content = self.html_processor.find(r'<dt[^>]*>竣工日</dt>\s*<dd[^>]*>(.*?)</dd>', html)
            if not construction_content:
                print("⚠️ No construction date section found")
                return
            
            construction_text = self.html_processor.clean_html(construction_content)
            year_pattern = self.html_processor.compile_regex(r'(\d{4})年')
            year_match = year_pattern.search(construction_text)
            
            if year_match:
                data['year'] = int(year_match.group(1))
            else:
                print(f"⚠️ Could not extract year from: {construction_text}")
                
        except Exception as e:
            print(f"❌ Error extracting construction date: {e}")
    
    def extract_structure_info(self, data: Dict[str, Any], html: str):
        """Extract building structure information with mapping"""
        try:
            structure_content = self.html_processor.find(r'<dt[^>]*>規模構造</dt>\s*<dd[^>]*>(.*?)</dd>', html)
            if not structure_content:
                print("⚠️ No structure section found")
                return
            
            structure_text = self.html_processor.clean_html(structure_content)
            print(f"🏗️ Structure text: '{structure_text}'")
            
            pattern = self.html_processor.compile_regex(r'^(.*?造)\s*地上(\d+)階(?:地下(\d+)階建?)?')
            match = pattern.search(structure_text)
            
            def map_structure(original_structure: str) -> str:
                if not original_structure:
                    return "other"

                keys = list(STRUCTURE_MAPPING.keys())
                # Tìm key giống nhất, cutoff = 0.5 để tránh match lung tung
                matches = difflib.get_close_matches(original_structure, keys, n=1, cutoff=0.5)

                if matches:
                    return STRUCTURE_MAPPING[matches[0]]
                return "other"
     
            if match:
                original_structure = match.group(1).strip()
                
                # Map structure using STRUCTURE_MAPPING
                mapped_structure = map_structure(original_structure)
                
                data.update({
                    'structure': mapped_structure,
                    'floors': int(match.group(2))
                })
                
                if match.group(3):
                    data['basement_floors'] = int(match.group(3))
                    
                print(f"🏗️ Mapped structure: '{original_structure}' → '{mapped_structure}'")
            else:
                print(f"⚠️ Structure pattern did not match: '{structure_text}'")
                
        except Exception as e:
            print(f"❌ Error extracting structure info: {e}")
    
    def extract_renewal_fee(self, data: Dict[str, Any], html: str):
        """Extract renewal fee information"""
        try:
            renewal_content = self.html_processor.find(r'<dt[^>]*>更新料</dt>\s*<dd[^>]*>(.*?)</dd>', html)
            if not renewal_content:
                print("⚠️ No renewal fee section found")
                return
            
            renewal_text = self.html_processor.clean_html(renewal_content)
            pattern = self.html_processor.compile_regex(r'新賃料の(\d+)ヶ月分')
            match = pattern.search(renewal_text)
            
            if match:
                months = int(match.group(1))
                data.update({
                    'renewal_new_rent': 'Y',
                    'months_renewal': 12 if months == 1 else months
                })
                
        except Exception as e:
            print(f"❌ Error extracting renewal fee: {e}")
    
    def extract_direction_info(self, data: Dict[str, Any], html: str):
        """Extract apartment facing direction"""
        try:
            direction_content = self.html_processor.find(r'<dt[^>]*>方位</dt>\s*<dd[^>]*>(.*?)</dd>', html)
            if not direction_content:
                print("⚠️ No direction section found")
                return
            
            direction_text = self.html_processor.clean_html(direction_content)
            
            for jp_direction, field_name in DIRECTION_MAPPING.items():
                if jp_direction in direction_text:
                    data[field_name] = 'Y'
                    break
            else:
                print(f"⚠️ No recognizable directions found in: {direction_text}")
                
        except Exception as e:
            print(f"❌ Error extracting direction info: {e}")
    
    def extract_lock_exchange(self, data: Dict[str, Any], html: str):
        """Extract lock exchange fee"""
        try:
            other_fees_content = self.html_processor.find(r'<dt[^>]*>その他費用</dt>\s*<dd[^>]*>(.*?)</dd>', html)
            if not other_fees_content:
                print("⚠️ No other fees section found")
                return
            
            other_fees_text = self.html_processor.clean_html(other_fees_content)
            
            data['property_other_expenses_ja'] = other_fees_text
            
            pattern = self.html_processor.compile_regex(r'玄関錠交換代[^\d]*([\d,]+)円')
            match = pattern.search(other_fees_text)
            
            if match:
                data['lock_exchange'] = int(match.group(1).replace(',', ''))
                
        except Exception as e:
            print(f"❌ Error extracting lock exchange: {e}")
    
    def extract_amenities(self, data: Dict[str, Any], html: str):
        """Extract amenities information"""
        try:
            amenities_pattern = self.html_processor.compile_regex(r'<dt[^>]*>専有部・共用部設備</dt>\s*<dd[^>]*>(.*?)</dd>')
            amenities_match = amenities_pattern.search(html)
            
            if not amenities_match:
                print("⚠️ No amenities section found")
                return
            
            amenities_text = self.html_processor.clean_html(amenities_match.group(1))
            print(f"🏢 Found amenities info: {amenities_text}")
            
            found_amenities = []
            for jp_amenity, field_name in AMENITIES_MAPPING.items():
                if jp_amenity in amenities_text:
                    data[field_name] = 'Y'
                    found_amenities.append(f"{jp_amenity} → {field_name}")
            
            if found_amenities:
                print(f"🏢 Set amenities to Y:")
                for amenity in found_amenities:
                    print(f"   {amenity}")
            else:
                print(f"⚠️ No recognizable amenities found")
                
        except Exception as e:
            print(f"❌ Error extracting amenities: {e}")
    
    def extract_building_description(self, data: Dict[str, Any], html: str):
        """Extract building description"""
        try:
            description_pattern = self.html_processor.compile_regex(r'<dt[^>]*>備考</dt>\s*<dd[^>]*>(.*?)</dd>')
            description_match = description_pattern.search(html)
            
            if description_match:
                description_text = self.html_processor.clean_html(description_match.group(1))
                if description_text:
                    data['building_description_ja'] = description_text
                    
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
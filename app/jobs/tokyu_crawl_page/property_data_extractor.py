"""
Property data extraction utilities for Tokyu crawling
Optimized version with helper methods and grouped extraction
"""
from typing import Dict, Any, Optional

from app.utils.html_processor_utils import HtmlProcessor
from app.utils.structure_utils import extract_structure_info
from app.utils.construction_date_utils import extract_construction_year
from app.utils.direction_utils import extract_direction_info
from app.utils.available_date_utils import extract_available_from
from app.utils.numeric_utils import extract_numeric_value, extract_months_multiplier, extract_area_size
from app.utils.amenities_utils import apply_amenities_to_data
from app.utils.property_utils import PropertyUtils
from app.utils.floor_utils import extract_floor_info
from app.jobs.tokyu_crawl_page.constants import DEFAULT_AMENITIES
from app.services.station_service import Station_Service
from app.utils.building_type_utils import extract_building_type


class PropertyDataExtractor:
    """Handles extraction of property data from HTML with optimized methods"""
    
    def __init__(self):
        self.html_processor = HtmlProcessor()
        self.station_service = Station_Service
    
    # ==================== HELPER METHODS ====================
    
    def _find_dt_dd(self, html: str, dt_label: str) -> Optional[str]:
        """Helper: Find and clean content from <dt>label</dt><dd>content</dd> pattern"""
        return self.html_processor.find_dt_dd(html, dt_label)
    
    def _find_td(self, html: str, th_label: str) -> Optional[str]:
        """Helper: Find and clean content from table <th>label</th>...<td>content</td> pattern"""
        return self.html_processor.find_td(html, th_label)
    
    def set_default_amenities(self, data: Dict[str, Any], html: str) -> Dict[str, Any]:
        """Set default amenities using global constants"""
        return PropertyUtils.set_default_amenities(data, DEFAULT_AMENITIES)
    
    def extract_building_info(self, data: Dict[str, Any], html: str) -> Dict[str, Any]:
        """Extract building-related information (name, type, structure, address, year)"""
        
        # Extract building_name_ja
        building_name = self._find_dt_dd(html, '物件名')
        if building_name:
            data['building_name_ja'] = building_name
            print(f"🏢 Building name: {building_name}")
        
        # Extract building_type
        building_type = self._find_dt_dd(html, '種別')
        if building_type:
            data['building_type'] = extract_building_type(building_type)
            print(f"🏗️ Building type: {data['building_type']}")
        
        # Extract structure
        structure_text = self._find_dt_dd(html, '建物構造')
        if structure_text:
            data['structure'] = extract_structure_info(structure_text)
            print(f"🏗️ Structure: {structure_text} -> {data['structure']}")
        
        # Extract address
        address = self._find_dt_dd(html, '所在地')
        if address:
            data['address'] = address
            print(f"📍 Address: {address}")
        
        # Extract year
        construction_text = self._find_dt_dd(html, '築年月')
        if construction_text:
            year = extract_construction_year(construction_text)
            if year:
                data['year'] = year
                print(f"📅 Construction year: {construction_text} -> {year}")
        
        return data
    
    def extract_unit_description(self, data: Dict[str, Any], html: str) -> Dict[str, Any]:
        description_parts = []
        
        # Tìm ペット可区分 và lấy nội dung thẻ td sau nó
        pet_content = self.html_processor.find(r'ペット可区分.*?<td[^>]*>(.*?)</td>', html)
        if pet_content:
            # Tìm tất cả các thẻ <li> trong nội dung
            li_pattern = self.html_processor.compile_regex(r'<li[^>]*>(.*?)</li>')
            li_matches = li_pattern.findall(pet_content)
            
            if li_matches and len(li_matches) > 1:
                # Bỏ qua thẻ li đầu tiên, lấy các thẻ còn lại
                remaining_lis = li_matches[1:]
                # Làm sạch HTML và nối các phần lại
                pet_text = ''.join([self.html_processor.clean_html(li).strip() for li in remaining_lis])
                if pet_text:
                    description_parts.append(pet_text)
                    print(f"🐾 Pet info: {pet_text}")
        
        # Tìm 備考 và lấy nội dung thẻ td sau nó
        remarks_content = self.html_processor.find(r'備考.*?<td[^>]*>(.*?)</td>', html)
        if remarks_content:
            remarks_text = self.html_processor.clean_html(remarks_content).strip()
            if remarks_text:
                description_parts.append(remarks_text)
                print(f"📝 Remarks: {remarks_text[:100]}...")
        
        # Kết hợp các phần với dấu xuống dòng
        if description_parts:
            data['property_description_ja'] = ' \n '.join(description_parts)
            print(f"📄 Property description: {data['property_description_ja'][:150]}...")
        
        return data
    
    def extract_unit_info(self, data: Dict[str, Any], html: str) -> Dict[str, Any]:
        """Extract unit-related information (unit_no, floor, size, direction)"""
        
        # Extract unit_no
        unit_no = self._find_td(html, '部屋番号')
        if unit_no:
            data['unit_no'] = unit_no
            print(f"🚪 Unit no: {unit_no}")
        
        # Extract floors/floor_no
        floor_text = self._find_td(html, '所在階/階建')
        if floor_text:
            floor_info = extract_floor_info(floor_text)
            data.update(floor_info)
            print(f"🏢 Floor info: {floor_text} -> {floor_info}")
        
        # Extract size
        size_text = self._find_td(html, '専有面積')
        if size_text:
            size = extract_area_size(size_text)
            data['size'] = size if size and size > 0 else 0
            print(f"📐 Size: {size_text} -> {data['size']}m²")
        else:
            data['size'] = 0
        
        # Extract facing direction
        direction_text = self._find_td(html, '方位')
        if direction_text:
            direction_info = extract_direction_info(direction_text)
            data.update(direction_info)
            print(f"🧭 Direction: {direction_text} -> {direction_info}")
        
        return data
    
    def extract_other_fee(self, data: Dict[str, Any], html: str) -> Dict[str, Any]:
        """Extract other fees (退去時費用) - cleaning fee and other expenses"""
        
        text = self._find_td(html, '退去時費用')
        if not text:
            return data
        
        print(f"💰 Other fees content: {text[:100]}...")
        
        # Extract cleaning fee
        cleaning_match = self.html_processor.compile_regex(r'清掃費[：:]\s*([0-9,]+)円').search(text)
        if cleaning_match:
            cleaning_fee = extract_numeric_value(cleaning_match.group(1).replace(',', '') + '円')
            data['other_initial_fees'] = cleaning_fee if cleaning_fee and cleaning_fee > 0 else 0
            print(f"💰 Cleaning fee: {cleaning_match.group(1)}円 -> {data['other_initial_fees']}")
        else:
            data['other_initial_fees'] = 0
        
        # Extract other expenses description
        lines = text.split('\n', 1)[1] if '\n' in text else ''
        if lines:
            data['property_other_expenses_ja'] = lines
        
        return data
            
    
    def extract_rental_costs(self, data: Dict[str, Any], html: str) -> Dict[str, Any]:
        """Extract rental cost information (rent, maintenance)"""
        
        # Extract monthly_rent (special case: needs span tag)
        rent_content = self.html_processor.find(r'賃料.*?<td[^>]*>.*?<span[^>]*>(.*?)</span>', html)
        if rent_content:
            rent_text = self.html_processor.clean_html(rent_content).strip()
            monthly_rent = extract_numeric_value(rent_text)
            data['monthly_rent'] = monthly_rent if monthly_rent and monthly_rent > 0 else 0
            print(f"💰 Monthly rent: {rent_text} -> {data['monthly_rent']}円")
        else:
            data['monthly_rent'] = 0
        
        # Extract monthly_maintenance
        maintenance_text = self._find_td(html, '管理費・共益費')
        if maintenance_text:
            monthly_maintenance = extract_numeric_value(maintenance_text)
            data['monthly_maintenance'] = monthly_maintenance if monthly_maintenance is not None else 0
            print(f"💰 Monthly maintenance: {maintenance_text} -> {data['monthly_maintenance']}円")
        else:
            data['monthly_maintenance'] = 0
        
        return data
    
    def extract_deposits_and_fees(self, data: Dict[str, Any], html: str) -> Dict[str, Any]:
        """Extract deposit and fee information (deposit, key money, renewal fee)"""
        
        # Initialize all numeric fields to 0
        data.setdefault('numeric_deposit', 0)
        data.setdefault('numeric_security_deposit', 0)
        data.setdefault('numeric_key', 0)
        data.setdefault('numeric_deposit_amortization', 0)
        data.setdefault('numeric_renewal', 0)
        
        monthly_rent = data.get('monthly_rent', 0)
        
        # Extract deposit (敷金/保証金)
        deposit_text = self._find_td(html, '敷金/保証金')
        if deposit_text:
            parts = deposit_text.split('/')
            if len(parts) >= 1:
                deposit_months = extract_months_multiplier(parts[0].strip())
                if deposit_months and deposit_months > 0 and monthly_rent:
                    data['numeric_deposit'] = int(deposit_months * monthly_rent)
                    print(f"💰 Deposit: {parts[0].strip()} -> {data['numeric_deposit']}円")
            
            if len(parts) >= 2:
                security_months = extract_months_multiplier(parts[1].strip())
                if security_months and security_months > 0 and monthly_rent:
                    data['numeric_security_deposit'] = int(security_months * monthly_rent)
                    print(f"💰 Security deposit: {parts[1].strip()} -> {data['numeric_security_deposit']}円")
        
        # Extract key money (礼金/償却・敷引)
        key_text = self._find_td(html, '礼金/償却・敷引')
        if key_text:
            parts = key_text.split('/')
            if len(parts) >= 1:
                key_months = extract_months_multiplier(parts[0].strip())
                if key_months and key_months > 0 and monthly_rent:
                    data['numeric_key'] = int(key_months * monthly_rent)
                    print(f"💰 Key money: {parts[0].strip()} -> {data['numeric_key']}円")
            
            if len(parts) >= 2:
                amortization_months = extract_months_multiplier(parts[1].strip())
                if amortization_months and amortization_months > 0 and monthly_rent:
                    data['numeric_deposit_amortization'] = int(amortization_months * monthly_rent)
                    print(f"💰 Deposit amortization: {parts[1].strip()} -> {data['numeric_deposit_amortization']}円")
        
        # Extract renewal fee (更新料)
        renewal_text = self._find_td(html, '更新料')
        if renewal_text:
            renewal_months = extract_months_multiplier(renewal_text)
            if renewal_months and renewal_months > 0 and monthly_rent:
                data['numeric_renewal'] = int(renewal_months * monthly_rent)
                print(f"💰 Renewal fee: {renewal_text} -> {data['numeric_renewal']}円")
        
        return data
    
    def extract_future(self, data: Dict[str, Any], html: str) -> Dict[str, Any]:
        """Extract amenities and features from 設備・条件 section"""
        amenities_text = self._find_td(html, '設備・条件')
        if not amenities_text:
            print("⚠️ No amenities section (設備・条件) found")
            return data
        
        print(f"🏢 Found amenities text: {amenities_text[:200]}...")
        apply_amenities_to_data(amenities_text, data)
        
        return data
    
    def extract_is_pets(self, data: Dict[str, Any], html: str) -> Dict[str, Any]:
        """Extract pet policy from 敷金積増 section"""
        deposit_increase_text = self._find_td(html, '敷金積増')
        
        if deposit_increase_text:
            print(f"🏠 Deposit increase text: {deposit_increase_text}")
            
            # Check if pets are mentioned
            if 'ペット飼育' in deposit_increase_text:
                if '有り' in deposit_increase_text or '有' in deposit_increase_text:
                    data['pets'] = 'Y'
                    print(f"🐕 Pets allowed: {deposit_increase_text} -> Y")
                elif '無し' in deposit_increase_text or '無' in deposit_increase_text:
                    data['pets'] = 'N'
                    print(f"🐕 Pets not allowed: {deposit_increase_text} -> N")
                else:
                    data['pets'] = 'Y'
                    print(f"🐕 Pets mentioned (assuming allowed): {deposit_increase_text} -> Y")
            else:
                data['pets'] = 'N'
                print(f"🐕 No pets mentioned: {deposit_increase_text} -> N")
        else:
            data['pets'] = 'N'
            print("🐕 No deposit increase section found -> pets: N")
        
        return data
    
    def extract_money(self, data: Dict[str, Any], html: str) -> Dict[str, Any]:
        """Calculate financial information (guarantor, agency, insurance, discount, availability)"""
        monthly_rent = data.get('monthly_rent', 0)
        monthly_maintenance = data.get('monthly_maintenance', 0)
        total_monthly = int(monthly_rent + monthly_maintenance)
        
        # Calculate guarantor and agency fees
        data['numeric_guarantor'] = total_monthly * 0.5
        data['numeric_guarantor_max'] = total_monthly
        data['numeric_agency'] = int(1.1 * monthly_rent)
        
        print(f"💰 Total monthly: {total_monthly}円")
        print(f"💰 Guarantor amount: {data['numeric_guarantor']}円")
        print(f"💰 Agency fee: {data['numeric_agency']}円")
        
        # Extract fire insurance (保険料)
        insurance_text = self._find_td(html, '保険料')
        if insurance_text:
            fire_insurance_amount = extract_numeric_value(insurance_text)
            if fire_insurance_amount and fire_insurance_amount > 0:
                data['fire_insurance'] = fire_insurance_amount * total_monthly
                print(f"🔥 Fire insurance: {insurance_text} -> {fire_insurance_amount}円")
            else:
                data['fire_insurance'] = 0
                print(f"🔥 Fire insurance: {insurance_text} (no numeric value found) -> 0")
        else:
            data['fire_insurance'] = 0
        
        # Extract discount (フリーレント)
        discount_text = self._find_td(html, 'フリーレント')
        if discount_text:
            discount_months = extract_months_multiplier(discount_text)
            if discount_months and discount_months > 0:
                data['numeric_discount'] = int(discount_months * monthly_rent)
                print(f"🎁 Discount: {discount_text} -> {data['numeric_discount']}円")
            else:
                data['numeric_discount'] = 0
        else:
            data['numeric_discount'] = 0
        
        # Extract available_from (入居可能日)
        available_text = self._find_td(html, '入居可能日')
        if available_text:
            available_date = extract_available_from(available_text)
            if available_date:
                data['available_from'] = available_date
                print(f"📅 Available from: {available_text} -> {available_date}")
        
        return data
    
    def extract_station(self, data: Dict[str, Any], html: str) -> Dict[str, Any]:
        """Extract nearby stations using StationService"""
        print("🗺️ Extracting station data...")
        return self.station_service.set_station_data(data, html)
    
    def cleanup_temp_fields(self, data: Dict[str, Any], html: str) -> Dict[str, Any]:
        """Remove temporary fields that shouldn't be in final JSON"""
        return PropertyUtils.cleanup_temp_fields(data, '_html')
"""
Property data extraction utilities for Tokyu crawling
"""
from typing import Dict, Any

from app.utils.html_processor_utils import HtmlProcessor
from app.utils.structure_utils import extract_structure_info
from app.utils.construction_date_utils import extract_construction_year
from app.utils.direction_utils import extract_direction_info
from app.utils.available_date_utils import extract_available_from
from app.utils.numeric_utils import extract_numeric_value, extract_months_multiplier, extract_area_size
from app.utils.amenities_utils import process_amenities_text, apply_amenities_to_data
from app.jobs.tokyu_crawl_page.constants import DEFAULT_AMENITIES, AMENITIES_MAPPING
from app.services.station_service import StationService
from app.utils.building_type_utils import extract_building_type


class PropertyDataExtractor:
    """Handles extraction of property data from HTML"""
    
    def __init__(self):
        self.html_processor = HtmlProcessor()
        self.station_service = StationService()
    
    def extract_floor_info(self, floor_text: str) -> Dict[str, int]:
        """
        Extract floor information from text (e.g., "1階/7階建" -> {"floor_no": 1, "floors": 7})
        
        Args:
            floor_text: Text containing floor information
            
        Returns:
            Dictionary with floor_no and floors
        """
        result = {}
        
        if not floor_text:
            return result
        
        # Pattern for "X階/Y階建"
        pattern = self.html_processor.compile_regex(r'(\d+)階/(\d+)階建')
        match = pattern.search(floor_text)
        
        if match:
            result['floor_no'] = int(match.group(1))
            result['floors'] = int(match.group(2))
        
        return result
    
    def set_default_amenities(self, data: Dict[str, Any], html: str) -> Dict[str, Any]:
        """Set default amenities using global constants"""
        data.update(DEFAULT_AMENITIES)
        return data
    
    def extract_building_info(self, data: Dict[str, Any], html: str) -> Dict[str, Any]:
        """Extract building-related information (name, type, structure, address, year)"""
        
        # Extract building_name_ja - Tìm 物件名 lấy nội dung thẻ dd sau nó
        building_name = self.html_processor.find(r'<dt[^>]*>\s*物件名\s*</dt>\s*<dd[^>]*>(.*?)</dd>', html)
        if building_name:
            data['building_name_ja'] = self.html_processor.clean_html(building_name).strip()
            print(f"🏢 Building name: {data['building_name_ja']}")
        
        # Extract building_type - Tìm 種別 lấy nội dung thẻ dd sau nó
        building_type = self.html_processor.find(r'種別.*?<dd[^>]*>(.*?)</dd>', html)
        if building_type:
            building_type = self.html_processor.clean_html(building_type).strip()
            data['building_type'] = extract_building_type(building_type)
            print(f"🏗️ Building type: {data['building_type']}")
        
        # Extract structure - Tìm 建物構造 lấy nội dung thẻ dd sau nó
        structure_content = self.html_processor.find(r'建物構造.*?<dd[^>]*>(.*?)</dd>', html)
        if structure_content:
            structure_text = self.html_processor.clean_html(structure_content).strip()
            data['structure'] = extract_structure_info(structure_text)
            print(f"🏗️ Structure: {structure_text} -> {data['structure']}")
        
        # Extract address - Tìm 所在地 lấy nội dung thẻ dd sau nó
        address = self.html_processor.find(r'所在地.*?<dd[^>]*>(.*?)</dd>', html)
        if address:
            data['address'] = self.html_processor.clean_html(address).strip()
            print(f"📍 Address: {data['address']}")
        
        # Extract year - Tìm 築年月 lấy nội dung thẻ dd sau nó
        construction_content = self.html_processor.find(r'築年月.*?<dd[^>]*>(.*?)</dd>', html)
        if construction_content:
            construction_text = self.html_processor.clean_html(construction_content).strip()
            year = extract_construction_year(construction_text)
            if year:
                data['year'] = year
                print(f"📅 Construction year: {construction_text} -> {year}")
        
        return data
    
    def extract_unit_description(self, data: Dict[str, Any], html: str) -> Dict[str, Any]:
        '''
        Tận dụng các hàm utils
        tìm ペット可区分  tìm thẻ td sau nó và loại bỏ thẻ li đầu tiên, còn lại sẽ được thêm vào trong data theo key property_description_ja
        Mẫu
        <td colspan="3"><ul><li class="fl mr_30">可</li><li class="fl mr_30">小型犬：可　／　大型犬：-　／　猫：可</li><li class="fl">小型犬・中型犬1匹または猫1匹</li></ul></td>
        => data[property_description_ja] = 小型犬：可　／　大型犬：-　／　猫：可小型犬・中型犬1匹または猫1匹
        
        Sau đó tiếp tục tìm 備考 lấy nội dung thẻ td sau nó:
        
        Lưu vào tiếp tục cho data[property_description_ja]
        Mẫu cuối cùng mong muốn nhận được 
        data[property_description_ja] = "小型犬：可　／　大型犬：-　／　猫：可小型犬・中型犬1匹または猫1匹 \n ■指定保証会社利用必須※一部法人契約除く・敷金賃料1ヶ月分積増■楽器演奏不可、事務所・SOHO利用不可■解約時室内清掃費及びエアコンクリーニング費用借主負担■ペット飼育可（小型犬・中型犬1匹または猫2匹まで）敷金賃料2ヶ月分■一部住戸にて民泊あり、ただし本住戸にて民泊利用禁止"
        
        '''
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
        
        # Extract unit_no - Tìm 部屋番号 lấy nội dung thẻ td sau nó
        unit_no = self.html_processor.find(r'部屋番号.*?<td[^>]*>(.*?)</td>', html)
        if unit_no:
            data['unit_no'] = self.html_processor.clean_html(unit_no).strip()
            print(f"🚪 Unit no: {data['unit_no']}")
        
        # Extract floors/floor_no - Tìm 所在階/階建 lấy nội dung thẻ td sau nó
        floor_content = self.html_processor.find(r'所在階/階建.*?<td[^>]*>(.*?)</td>', html)
        if floor_content:
            floor_text = self.html_processor.clean_html(floor_content).strip()
            floor_info = self.extract_floor_info(floor_text)
            data.update(floor_info)
            print(f"🏢 Floor info: {floor_text} -> {floor_info}")
        
        # Extract size - Tìm 専有面積 lấy nội dung thẻ td sau nó
        size_content = self.html_processor.find(r'専有面積.*?<td[^>]*>(.*?)</td>', html)
        if size_content:
            size_text = self.html_processor.clean_html(size_content).strip()
            size = extract_area_size(size_text)
            data['size'] = size if size and size > 0 else 0
            print(f"📐 Size: {size_text} -> {data['size']}m²")
        else:
            data['size'] = 0
        
        # Extract facing direction - Tìm 方位 và lấy nội dung sau nó
        direction_content = self.html_processor.find(r'方位.*?<td[^>]*>(.*?)</td>', html)
        if direction_content:
            direction_text = self.html_processor.clean_html(direction_content).strip()
            direction_info = extract_direction_info(direction_text)
            data.update(direction_info)
            print(f"🧭 Direction: {direction_text} -> {direction_info}")
        
        return data
    
    def extract_other_fee(self, data: Dict[str, Any], html: str) -> Dict[str, Any]:
        """Extract other fees (退去時費用) - cleaning fee and other expenses"""
        
        # Tìm 退去時費用 và lấy nội dung thẻ td sau nó
        content = self.html_processor.find(r'退去時費用.*?<td[^>]*>(.*?)</td>', html)
        if not content:
            return data
        
        # Làm sạch HTML
        text = self.html_processor.clean_html(content).strip()
        if not text:
            return data
        
        print(f"💰 Other fees content: {text[:100]}...")
        
        # Trích xuất 清掃費 (cleaning fee) cho other_initial_fees
        cleaning_match = self.html_processor.compile_regex(r'清掃費[：:]\s*([0-9,]+)円').search(text)
        if cleaning_match:
            cleaning_fee = extract_numeric_value(cleaning_match.group(1).replace(',', '') + '円')
            data['other_initial_fees'] = cleaning_fee if cleaning_fee and cleaning_fee > 0 else 0
            print(f"💰 Cleaning fee: {cleaning_match.group(1)}円 -> {data['other_initial_fees']}")
        else:
            data['other_initial_fees'] = 0
        
        lines = text.split('\n', 1)[1] if '\n' in text else ''
        
        if lines:
            data['property_other_expenses_ja'] = lines
        
        return data
            
    
    def extract_rental_costs(self, data: Dict[str, Any], html: str) -> Dict[str, Any]:
        """Extract rental cost information (rent, maintenance)"""
        
        # Extract monthly_rent - Tìm 賃料 lấy nội dung thẻ td>span sau nó
        rent_content = self.html_processor.find(r'賃料.*?<td[^>]*>.*?<span[^>]*>(.*?)</span>', html)
        if rent_content:
            rent_text = self.html_processor.clean_html(rent_content).strip()
            monthly_rent = extract_numeric_value(rent_text)
            data['monthly_rent'] = monthly_rent if monthly_rent and monthly_rent > 0 else 0
            print(f"💰 Monthly rent: {rent_text} -> {data['monthly_rent']}円")
        else:
            data['monthly_rent'] = 0
        
        # Extract monthly_maintenance - Tìm 管理費・共益費 lấy nội dung thẻ td sau nó
        maintenance_content = self.html_processor.find(r'管理費・共益費.*?<td[^>]*>(.*?)</td>', html)
        if maintenance_content:
            maintenance_text = self.html_processor.clean_html(maintenance_content).strip()
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
        
        # Extract deposit - Tìm 敷金/保証金 lấy nội dung thẻ td sau nó
        deposit_content = self.html_processor.find(r'敷金/保証金.*?<td[^>]*>(.*?)</td>', html)
        if deposit_content:
            deposit_text = self.html_processor.clean_html(deposit_content).strip()
            # Split by / to get both values
            parts = deposit_text.split('/')
            if len(parts) >= 1:
                deposit_months = extract_months_multiplier(parts[0].strip())
                if deposit_months and deposit_months > 0 and 'monthly_rent' in data and data['monthly_rent']:
                    data['numeric_deposit'] = int(deposit_months * data['monthly_rent'])
                    print(f"💰 Deposit: {parts[0].strip()} -> {data['numeric_deposit']}円")
            
            if len(parts) >= 2:
                security_months = extract_months_multiplier(parts[1].strip())
                if security_months and security_months > 0 and 'monthly_rent' in data and data['monthly_rent']:
                    data['numeric_security_deposit'] = int(security_months * data['monthly_rent'])
                    print(f"💰 Security deposit: {parts[1].strip()} -> {data['numeric_security_deposit']}円")
        
        # Extract key money - Tìm 礼金/償却・敷引 và lấy nội dung thẻ td sau nó
        key_content = self.html_processor.find(r'礼金/償却・敷引.*?<td[^>]*>(.*?)</td>', html)
        if key_content:
            key_text = self.html_processor.clean_html(key_content).strip()
            # Split by / to get both values
            parts = key_text.split('/')
            if len(parts) >= 1:
                key_months = extract_months_multiplier(parts[0].strip())
                if key_months and key_months > 0 and 'monthly_rent' in data and data['monthly_rent']:
                    data['numeric_key'] = int(key_months * data['monthly_rent'])
                    print(f"💰 Key money: {parts[0].strip()} -> {data['numeric_key']}円")
            
            if len(parts) >= 2:
                amortization_months = extract_months_multiplier(parts[1].strip())
                if amortization_months and amortization_months > 0 and 'monthly_rent' in data and data['monthly_rent']:
                    data['numeric_deposit_amortization'] = int(amortization_months * data['monthly_rent'])
                    print(f"💰 Deposit amortization: {parts[1].strip()} -> {data['numeric_deposit_amortization']}円")
        
        # Extract renewal fee - Tìm 更新料 và lấy thẻ td sau nó
        renewal_content = self.html_processor.find(r'更新料.*?<td[^>]*>(.*?)</td>', html)
        if renewal_content:
            renewal_text = self.html_processor.clean_html(renewal_content).strip()
            renewal_months = extract_months_multiplier(renewal_text)
            if renewal_months and renewal_months > 0 and 'monthly_rent' in data and data['monthly_rent']:
                data['numeric_renewal'] = int(renewal_months * data['monthly_rent'])
                print(f"💰 Renewal fee: {renewal_text} -> {data['numeric_renewal']}円")
        
        return data
    
    def extract_future(self, data: Dict[str, Any], html: str) -> Dict[str, Any]:
        try:
            # Tìm 設備・条件 và lấy nội dung thẻ td sau nó
            amenities_content = self.html_processor.find(r'設備・条件.*?<td[^>]*>(.*?)</td>', html)
            if not amenities_content:
                print("⚠️ No amenities section (設備・条件) found")
                return data
            
            # Làm sạch HTML và lấy text
            amenities_text = self.html_processor.clean_html(amenities_content)
            if not amenities_text:
                print("⚠️ Amenities content is empty after cleaning")
                return data
            
            print(f"🏢 Found amenities text: {amenities_text[:200]}...")
            
            # Xử lý amenities bằng utils
            found_amenities = process_amenities_text(amenities_text, AMENITIES_MAPPING)
            
            if found_amenities:
                # Áp dụng amenities vào data
                apply_amenities_to_data(data, found_amenities)
                
                print(f"🏢 Set {len(found_amenities)} amenities to Y:")
                for amenity in found_amenities:
                    print(f"   {amenity['japanese']} → {amenity['field']}")
            else:
                print(f"⚠️ No recognizable amenities found in text")
                
        except Exception as e:
            print(f"❌ Error extracting amenities: {e}")
        
        return data
    
    def extract_is_pets(self, data: Dict[str, Any], html: str) -> Dict[str, Any]:
        '''
        Tìm 敷金積増 lấy nội dung thẻ td sau nó, mẫu 有り：ペット飼育
        đánh dấy data['pets'] = ?
        '''
        try:
            # Tìm 敷金積増 và lấy nội dung thẻ td sau nó
            deposit_increase_content = self.html_processor.find(r'敷金積増.*?<td[^>]*>(.*?)</td>', html)
            if deposit_increase_content:
                deposit_increase_text = self.html_processor.clean_html(deposit_increase_content).strip()
                print(f"🏠 Deposit increase text: {deposit_increase_text}")
                
                # Kiểm tra xem có chứa "ペット飼育" (pet keeping) hay không
                if 'ペット飼育' in deposit_increase_text:
                    # Kiểm tra xem có "有り" (có) hay "無し" (không có)
                    if '有り' in deposit_increase_text or '有' in deposit_increase_text:
                        data['pets'] = 'Y'
                        print(f"🐕 Pets allowed: {deposit_increase_text} -> Y")
                    elif '無し' in deposit_increase_text or '無' in deposit_increase_text:
                        data['pets'] = 'N'
                        print(f"🐕 Pets not allowed: {deposit_increase_text} -> N")
                    else:
                        # Nếu có mention ペット飼育 nhưng không rõ có hay không, mặc định là có
                        data['pets'] = 'Y'
                        print(f"🐕 Pets mentioned (assuming allowed): {deposit_increase_text} -> Y")
                else:
                    # Nếu không có mention về pets, mặc định là không cho phép
                    data['pets'] = 'N'
                    print(f"🐕 No pets mentioned: {deposit_increase_text} -> N")
            else:
                # Nếu không tìm thấy section 敷金積増, mặc định là không cho phép pets
                data['pets'] = 'N'
                print("🐕 No deposit increase section found -> pets: N")
                
        except Exception as e:
            print(f"❌ Error extracting pets info: {e}")
            # Trong trường hợp lỗi, mặc định là không cho phép pets
            data['pets'] = 'N'
        
        return data
    
    def extract_money(self, data: Dict[str, Any], html: str) -> Dict[str, Any]:
        monthly_rent = data['monthly_rent']
        monthly_maintenance = data['monthly_maintenance']
        
        total_monthly = int(monthly_rent + monthly_maintenance)
        
        data['numeric_guarantor'] = total_monthly * 0.5
        data['numeric_guarantor_max'] = total_monthly
        
        data['numeric_agency'] = int(1.1 * monthly_rent)
        
        print(f"💰 Total monthly: {total_monthly}円")
        print(f"💰 Guarantor amount: {data['numeric_guarantor']}円")
        print(f"💰 Agency fee: {data['numeric_agency']}円")
        
        """Extract additional information (insurance, discount, availability)"""
        
        # Extract fire insurance - Tìm 保険料 và lấy nội dung thẻ td sau nó
        insurance_content = self.html_processor.find(r'保険料.*?<td[^>]*>(.*?)</td>', html)
        if insurance_content:
            insurance_text = self.html_processor.clean_html(insurance_content).strip()
            # Extract numeric value from insurance text (e.g., "要 16,550円 2年" -> 16550)
            fire_insurance_amount = extract_numeric_value(insurance_text)
            if fire_insurance_amount and fire_insurance_amount > 0:
                data['fire_insurance'] = fire_insurance_amount * total_monthly
                print(f"🔥 Fire insurance: {insurance_text} -> {fire_insurance_amount}円")
            else:
                data['fire_insurance'] = 0
                print(f"🔥 Fire insurance: {insurance_text} (no numeric value found) -> 0")
        else:
            data['fire_insurance'] = 0
        
        # Extract discount - Tìm フリーレント và lấy nội dung thẻ td sau nó
        discount_content = self.html_processor.find(r'フリーレント.*?<td[^>]*>(.*?)</td>', html)
        if discount_content:
            discount_text = self.html_processor.clean_html(discount_content).strip()
            discount_months = extract_months_multiplier(discount_text)
            if discount_months and discount_months > 0 and 'monthly_rent' in data:
                data['numeric_discount'] = int(discount_months * monthly_rent)
                print(f"🎁 Discount: {discount_text} -> {data['numeric_discount']}円")
            else:
                data['numeric_discount'] = 0
        else:
            data['numeric_discount'] = 0
        
        # Extract available_from - Tìm 入居可能日 và lấy nội dung thẻ td sau nó
        available_content = self.html_processor.find(r'入居可能日.*?<td[^>]*>(.*?)</td>', html)
        if available_content:
            available_text = self.html_processor.clean_html(available_content).strip()
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
        if '_html' in data:
            del data['_html']
            print("🧹 Cleaned up temporary _html field")
        return data
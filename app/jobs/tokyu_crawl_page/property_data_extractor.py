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
    
    def __init__(self):
        self.html_processor = HtmlProcessor()
        self.station_service = Station_Service
        self._dt_dd_cache = None
        self._th_td_cache = None
    
    def _parse_html_once(self, html: str) -> None:
        if self._dt_dd_cache is None:
            self._dt_dd_cache = self.html_processor.parse_all_dt_dd(html)
        if self._th_td_cache is None:
            self._th_td_cache = self.html_processor.parse_all_th_td(html)
    
    def _get_dt_dd(self, dt_label: str) -> Optional[str]:
        return self._dt_dd_cache.get(dt_label) if self._dt_dd_cache else None
    
    def _get_td(self, th_label: str) -> Optional[str]:
        if not self._th_td_cache:
            return None
        content = self._th_td_cache.get(th_label)
        return self.html_processor.clean_html(content) if content else None
    
    def _get_td_raw(self, th_label: str) -> Optional[str]:
        return self._th_td_cache.get(th_label) if self._th_td_cache else None
    
    def _find_dt_dd(self, html: str, dt_label: str) -> Optional[str]:
        return self.html_processor.find_dt_dd(html, dt_label)
    
    def _find_td(self, html: str, th_label: str) -> Optional[str]:
        return self.html_processor.find_td(html, th_label)
    
    def set_default_amenities(self, data: Dict[str, Any], html: str) -> Dict[str, Any]:
        return PropertyUtils.set_default_amenities(data, DEFAULT_AMENITIES)
    
    def extract_building_info(self, data: Dict[str, Any], html: str) -> Dict[str, Any]:
        self._parse_html_once(html)
        
        if building_name := self._get_dt_dd('物件名'):
            data['building_name_ja'] = building_name
        
        if building_type := self._get_dt_dd('種別'):
            data['building_type'] = extract_building_type(building_type)
        
        if structure_text := self._get_dt_dd('建物構造'):
            data['structure'] = extract_structure_info(structure_text)
        
        if address := self._get_dt_dd('所在地'):
            data['address'] = address
        
        if construction_text := self._get_dt_dd('築年月'):
            if year := extract_construction_year(construction_text):
                data['year'] = year
        
        return data
    
    def extract_unit_description(self, data: Dict[str, Any], html: str) -> Dict[str, Any]:
        description_parts = []
        
        if pet_content := self.html_processor.find(r'ペット可区分.*?<td[^>]*>(.*?)</td>', html):
            li_pattern = self.html_processor.compile_regex(r'<li[^>]*>(.*?)</li>')
            if (li_matches := li_pattern.findall(pet_content)) and len(li_matches) > 1:
                pet_text = ''.join([self.html_processor.clean_html(li).strip() for li in li_matches[1:]])
                if pet_text:
                    description_parts.append(pet_text)
        
        if remarks_content := self.html_processor.find(r'備考.*?<td[^>]*>(.*?)</td>', html):
            if remarks_text := self.html_processor.clean_html(remarks_content).strip():
                description_parts.append(remarks_text)
        
        if description_parts:
            data['property_description_ja'] = ' \n '.join(description_parts)
        
        return data
    
    def extract_unit_info(self, data: Dict[str, Any], html: str) -> Dict[str, Any]:
        self._parse_html_once(html)
        
        if unit_no := self._get_td('部屋番号'):
            data['unit_no'] = unit_no
        
        if floor_text := self._get_td('所在階/階建'):
            data.update(extract_floor_info(floor_text))
        
        if size_text := self._get_td('専有面積'):
            size = extract_area_size(size_text)
            data['size'] = size if size and size > 0 else 0
        else:
            data['size'] = 0
        
        if direction_text := self._get_td('方位'):
            data.update(extract_direction_info(data, direction_text))
        
        return data
    
    def extract_other_fee(self, data: Dict[str, Any], html: str) -> Dict[str, Any]:
        self._parse_html_once(html)
        
        if not (text := self._get_td('退去時費用')):
            return data
        
        if cleaning_match := self.html_processor.compile_regex(r'清掃費[：:]\s*([0-9,]+)円').search(text):
            cleaning_fee = extract_numeric_value(cleaning_match.group(1).replace(',', '') + '円')
            data['other_initial_fees'] = cleaning_fee if cleaning_fee and cleaning_fee > 0 else 0
        else:
            data['other_initial_fees'] = 0
        
        if lines := (text.split('\n', 1)[1] if '\n' in text else ''):
            data['property_other_expenses_ja'] = lines
        
        return data
            
    
    def extract_rental_costs(self, data: Dict[str, Any], html: str) -> Dict[str, Any]:
        self._parse_html_once(html)
        
        if rent_content_raw := self._get_td_raw('賃料'):
            if span_match := self.html_processor.compile_regex(r'<span[^>]*>(.*?)</span>').search(rent_content_raw):
                rent_text = self.html_processor.clean_html(span_match.group(1)).strip()
                monthly_rent = extract_numeric_value(rent_text)
                data['monthly_rent'] = monthly_rent if monthly_rent and monthly_rent > 0 else 0
            else:
                data['monthly_rent'] = 0
        else:
            data['monthly_rent'] = 0
        
        if maintenance_text := self._get_td('管理費・共益費'):
            monthly_maintenance = extract_numeric_value(maintenance_text)
            data['monthly_maintenance'] = monthly_maintenance if monthly_maintenance is not None else 0
        else:
            data['monthly_maintenance'] = 0
        
        return data
    
    def extract_deposits_and_fees(self, data: Dict[str, Any], html: str) -> Dict[str, Any]:
        self._parse_html_once(html)
        
        data.setdefault('numeric_deposit', 0)
        data.setdefault('numeric_security_deposit', 0)
        data.setdefault('numeric_key', 0)
        data.setdefault('numeric_deposit_amortization', 0)
        data.setdefault('numeric_renewal', 0)
        
        monthly_rent = data.get('monthly_rent', 0)
        
        if deposit_text := self._get_td('敷金/保証金'):
            parts = deposit_text.split('/')
            if len(parts) >= 1 and (deposit_months := extract_months_multiplier(parts[0].strip())) and deposit_months > 0 and monthly_rent:
                data['numeric_deposit'] = int(deposit_months * monthly_rent)
            if len(parts) >= 2 and (security_months := extract_months_multiplier(parts[1].strip())) and security_months > 0 and monthly_rent:
                data['numeric_security_deposit'] = int(security_months * monthly_rent)
        
        if key_text := self._get_td('礼金/償却・敷引'):
            parts = key_text.split('/')
            if len(parts) >= 1 and (key_months := extract_months_multiplier(parts[0].strip())) and key_months > 0 and monthly_rent:
                data['numeric_key'] = int(key_months * monthly_rent)
            if len(parts) >= 2 and (amortization_months := extract_months_multiplier(parts[1].strip())) and amortization_months > 0 and monthly_rent:
                data['numeric_deposit_amortization'] = int(amortization_months * monthly_rent)
        
        if renewal_text := self._get_td('更新料'):
            if (renewal_months := extract_months_multiplier(renewal_text)) and renewal_months > 0 and monthly_rent:
                data['numeric_renewal'] = int(renewal_months * monthly_rent)
        
        return data
    
    def extract_future(self, data: Dict[str, Any], html: str) -> Dict[str, Any]:
        self._parse_html_once(html)
        
        if amenities_text := self._get_td('設備・条件'):
            apply_amenities_to_data(amenities_text, data)
        
        return data
    
    def extract_is_pets(self, data: Dict[str, Any], html: str) -> Dict[str, Any]:
        self._parse_html_once(html)
        
        if deposit_increase_text := self._get_td('敷金積増'):
            if 'ペット飼育' in deposit_increase_text:
                data['pets'] = 'N' if '無し' in deposit_increase_text or '無' in deposit_increase_text else 'Y'
            else:
                data['pets'] = 'N'
        else:
            data['pets'] = 'N'
        
        return data
    
    def extract_money(self, data: Dict[str, Any], html: str) -> Dict[str, Any]:
        self._parse_html_once(html)
        
        monthly_rent = data.get('monthly_rent', 0)
        monthly_maintenance = data.get('monthly_maintenance', 0)
        total_monthly = int(monthly_rent + monthly_maintenance)
        
        data['numeric_guarantor'] = total_monthly * 0.5
        data['numeric_guarantor_max'] = total_monthly
        data['numeric_agency'] = int(1.1 * monthly_rent)
        
        if insurance_text := self._get_td('保険料'):
            if (fire_insurance_amount := extract_numeric_value(insurance_text)) and fire_insurance_amount > 0:
                data['fire_insurance'] = fire_insurance_amount * total_monthly
            else:
                data['fire_insurance'] = 0
        else:
            data['fire_insurance'] = 0
        
        if discount_text := self._get_td('フリーレント'):
            if (discount_months := extract_months_multiplier(discount_text)) and discount_months > 0:
                data['numeric_discount'] = int(discount_months * monthly_rent)
            else:
                data['numeric_discount'] = 0
        else:
            data['numeric_discount'] = 0
        
        if available_text := self._get_td('入居可能日'):
            if available_date := extract_available_from(available_text):
                data['available_from'] = available_date
        
        return data
    
    def extract_station(self, data: Dict[str, Any], html: str) -> Dict[str, Any]:
        return self.station_service.set_station_data(data, html)
    
    def cleanup_temp_fields(self, data: Dict[str, Any], html: str) -> Dict[str, Any]:
        self._dt_dd_cache = None
        self._th_td_cache = None
        return PropertyUtils.cleanup_temp_fields(data, '_html')
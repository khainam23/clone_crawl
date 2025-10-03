"""
Available date processing utilities
"""
import re
import calendar
from datetime import datetime, date
from app.utils.html_processor_utils import HtmlProcessor


def extract_available_from(available_text: str) -> str:
    """
    Extract and parse available from date
    
    Args:
        available_text: Raw available date text from HTML
        
    Returns:
        ISO format date string (yyyy-mm-dd) or None
    """
    html_processor = HtmlProcessor()
    
    if not available_text:
        return None

    current_year = datetime.now().year
    parsed_date = None

    if "即時" in available_text or "即可" in available_text:
        parsed_date = date.today()
    else:
        # 上旬/中旬/下旬 → ngày cố định
        for key, day in {"上旬": "10", "中旬": "20", "下旬": "28"}.items():
            available_text = re.sub(rf'(\d{{4}}年)?(\d{{1,2}})月{key}', 
                        lambda m: f"{m.group(1) or str(current_year)+'年'}{m.group(2)}月{day}日", 
                        available_text)

        # 月末 → ngày cuối tháng
        m = re.search(r'(\d{4})?年?(\d{1,2})月末', available_text)
        if m:
            year = int(m.group(1)) if m.group(1) else current_year
            month = int(m.group(2))
            last_day = calendar.monthrange(year, month)[1]
            available_text = f"{year}年{month}月{last_day}日"

        # regex patterns
        patterns = [
            (r'(\d{4})年(\d{1,2})月(\d{1,2})日', lambda y,m,d: date(int(y), int(m), int(d))),
            (r'(\d{1,2})月(\d{1,2})日',          lambda m,d: date(current_year, int(m), int(d))),
            (r'(\d{4})/(\d{1,2})/(\d{1,2})',   lambda y,m,d: date(int(y), int(m), int(d))),
            (r'(\d{1,2})/(\d{1,2})',           lambda m,d: date(current_year, int(m), int(d))),
        ]

        for pat, conv in patterns:
            m = re.search(pat, available_text)
            if m:
                try:
                    parsed_date = conv(*m.groups())
                    break
                except ValueError:
                    continue

    if parsed_date:
        return parsed_date.isoformat()
    
    return None
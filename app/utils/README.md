# Utils Package

Các utility functions hỗ trợ crawling và xử lý dữ liệu bất động sản.

## Modules

| Module | Mục đích | Functions chính |
|--------|----------|-----------------|
| `property_utils.py` | Xử lý property data | `validate_and_create_property_model()`, `create_crawl_result()`, `log_crawl_success()`, `log_crawl_error()` |
| `save_utils.py` | Database operations | `save_db_results()`, `clean_db()` |
| `validation_utils.py` | Data validation | `is_valid_url()`, `validate_property_data()`, `validate_urls()`, `clean_text()` |
| `city_utils.py` | Quản lý thành phố | `init()`, `get_city_by_id()` |
| `prefecture_utils.py` | Quản lý tỉnh | `init()`, `get_prefecture_by_id()` |
| `district_utils.py` | Geospatial queries | `get_district()` |

## Cách dùng

### 1. Property Operations
```python
from app.utils.property_utils import PropertyUtils

# Validate và tạo PropertyModel
property_model = PropertyUtils.validate_and_create_property_model(raw_data)

# Tạo crawl result
result = PropertyUtils.create_crawl_result(property_data=data)

# Log kết quả
PropertyUtils.log_crawl_success(url, data)
PropertyUtils.log_crawl_error(url, error)
```

### 2. Database Operations
```python
from app.utils.save_utils import SaveUtils

# Lưu vào MongoDB
await SaveUtils.save_db_results(results, "crawl_results", _id=0)

# Xóa dữ liệu
await SaveUtils.clean_db("crawl_results")
```

### 3. Data Validation
```python
from app.utils.validation_utils import ValidationUtils

# Validate URLs
valid_urls = ValidationUtils.validate_urls(url_list)

# Validate property data
clean_data = ValidationUtils.validate_property_data(raw_data)

# Kiểm tra URL
if ValidationUtils.is_valid_url(url):
    pass

# Clean text
clean_text = ValidationUtils.clean_text(messy_text)
```

### 4. Geospatial Operations
```python
from app.utils.city_utils import init as init_cities, get_city_by_id
from app.utils.prefecture_utils import init as init_prefectures, get_prefecture_by_id
from app.utils.district_utils import get_district

# Initialize data (chạy 1 lần khi khởi động app)
await init_cities()
await init_prefectures()

# Lookup theo ID (O(1))
city_name = get_city_by_id(123)
prefecture_name = get_prefecture_by_id(456)

# Tìm district theo tọa độ
district_info = get_district(lat=35.6762, lng=139.6503)  # Returns: [district, prefecture, city]
```

## Import

```python
# Core utilities
from app.utils.property_utils import PropertyUtils
from app.utils.save_utils import SaveUtils
from app.utils.validation_utils import ValidationUtils

# Geospatial utilities
from app.utils.city_utils import init as init_cities, get_city_by_id
from app.utils.prefecture_utils import init as init_prefectures, get_prefecture_by_id
from app.utils.district_utils import get_district
```

## Lưu ý

- **Geospatial data**: Cần init cities/prefectures trước khi sử dụng
- **Database**: Sử dụng MongoDB với 2dsphere index cho geospatial queries
- **Performance**: City/prefecture lookup là O(1) nhờ in-memory cache
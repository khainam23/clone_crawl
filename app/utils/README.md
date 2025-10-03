# Utils Package

Thư mục chứa các utility functions được tổ chức theo chức năng, hỗ trợ crawling và xử lý dữ liệu bất động sản.

## Modules

### `property_utils.py`
**PropertyUtils** - Xử lý property data:
- `validate_and_create_property_model()` - Validate và tạo PropertyModel
- `create_crawl_result()` - Tạo cấu trúc kết quả crawl
- `log_crawl_success()`, `log_crawl_error()` - Log kết quả crawl

### `save_utils.py`
**SaveUtils** - Database operations:
- `save_db_results()` - Lưu kết quả vào MongoDB
- `clean_db()` - Xóa dữ liệu trong collection

### `validation_utils.py`
**ValidationUtils** - Data validation:
- `is_valid_url()` - Kiểm tra URL hợp lệ
- `validate_property_data()` - Validate property data
- `validate_urls()` - Validate danh sách URLs
- `clean_text()` - Clean và normalize text

### `city_utils.py`
**City utilities** - Quản lý thông tin thành phố:
- `init()` - Load cities vào memory (O(1) lookup)
- `get_city_by_id()` - Lấy city theo ID

### `prefecture_utils.py`
**Prefecture utilities** - Quản lý thông tin tỉnh:
- `init()` - Load prefectures vào memory (O(1) lookup)
- `get_prefecture_by_id()` - Lấy prefecture theo ID

### `district_utils.py`
**District utilities** - Geospatial queries:
- `get_district()` - Tìm district gần nhất theo tọa độ (MongoDB 2dsphere)

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

# Package level import
from app.utils import PropertyUtils, SaveUtils, ValidationUtils
```

## Sử dụng

### Property Operations
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

### Database Operations
```python
from app.utils.save_utils import SaveUtils

# Lưu vào MongoDB
await SaveUtils.save_db_results(results, "crawl_results", _id=0)

# Xóa dữ liệu
await SaveUtils.clean_db("crawl_results")
```

### Data Validation
```python
from app.utils.validation_utils import ValidationUtils

# Validate URLs
valid_urls = ValidationUtils.validate_urls(url_list)

# Validate property data
clean_data = ValidationUtils.validate_property_data(raw_data)

# Kiểm tra URL
if ValidationUtils.is_valid_url(url):
    # Process URL
    pass

# Clean text
clean_text = ValidationUtils.clean_text(messy_text)
```

### Geospatial Operations
```python
from app.utils.city_utils import init as init_cities, get_city_by_id
from app.utils.prefecture_utils import init as init_prefectures, get_prefecture_by_id
from app.utils.district_utils import get_district

# Initialize data (chạy khi khởi động app)
await init_cities()
await init_prefectures()

# Lookup theo ID (O(1))
city_name = get_city_by_id(123)
prefecture_name = get_prefecture_by_id(456)

# Tìm district theo tọa độ
district_info = get_district(lat=35.6762, lng=139.6503)  # [district, prefecture, city]
```

## Tính năng

- **Property Processing**: Validate và xử lý dữ liệu property
- **Database Operations**: Lưu/xóa dữ liệu MongoDB với collection tùy chọn  
- **Data Validation**: Validate URLs và clean text data
- **Geospatial Support**: Tìm kiếm địa lý với MongoDB 2dsphere index
- **Performance**: O(1) lookup cho city/prefecture data
- **Logging**: Python logging chuẩn với multiple levels
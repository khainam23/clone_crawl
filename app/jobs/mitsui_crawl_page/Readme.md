# Mitsui Crawl Page

Module crawl dữ liệu bất động sản từ website Mitsui Chintai (https://www.mitsui-chintai.co.jp/).

## 🎯 Mục đích

Crawl thông tin chi tiết các căn phòng cho thuê từ trang web Mitsui Chintai, bao gồm:
- Thông tin cơ bản (giá, diện tích, địa chỉ)
- Hình ảnh phòng
- Tiện ích và đặc điểm
- Tọa độ địa lý
- Thông tin ga tàu gần nhất

## 📁 Cấu trúc Module (Optimized)

```
mitsui_crawl_page/
├── index.py                      # Entry point - Crawl URLs từ listing pages
├── constants.py                  # Constants và configurations
├── property_data_extractor.py    # Extract property data (Optimized)
├── image_extractor.py            # Extract images từ gallery
├── coordinate_converter.py       # Convert XY coordinates sang lat/lng
└── custom_extractor_factory.py  # Factory tạo CustomExtractor (Optimized)
```

## ✨ Cải tiến trong phiên bản Optimized

### 1. **PropertyDataExtractor** - Tối ưu hóa
- ✅ **Helper methods**: `_extract_dt_dd_content()` để tái sử dụng code
- ✅ **Safe extraction**: `_safe_extract()` với error handling tự động
- ✅ **Grouped extractors**: Tất cả extractors được gọi qua `get_static_info()`
- ✅ **Giảm code trùng lặp**: Từ 422 dòng xuống ~370 dòng
- ✅ **Dễ maintain**: Mỗi method chỉ làm 1 việc rõ ràng

### 2. **CustomExtractorFactory** - Đơn giản hóa
- ✅ **Clear pipeline**: Processing pipeline được document rõ ràng
- ✅ **Private methods**: `_create_safe_wrapper()`, `_pass_html()` 
- ✅ **Better naming**: Tên method rõ ràng hơn
- ✅ **Removed unused**: Loại bỏ StationService không dùng

### 3. **Index.py** - Cải thiện
- ✅ **Separated concerns**: `_fetch_page_urls()` tách riêng
- ✅ **Better error handling**: Timeout và exception handling
- ✅ **Progress logging**: Log rõ ràng từng bước
- ✅ **Type hints**: Thêm type hints cho parameters

## 🚀 Cách sử dụng

### Import và chạy crawl

```python
from app.jobs.mitsui_crawl_page.index import crawl_multi

# Chạy crawl multi-page
await crawl_multi()
```

### Cấu hình

Các cấu hình chính trong `constants.py`:
- `URL_MULTI`: URL trang danh sách
- `ITEM_SELECTOR`: CSS selector cho các item
- `NUM_PAGES`: Số trang cần crawl
- `ID_MONGO`: ID field trong MongoDB
- `COLLECTION_NAME`: Tên collection MongoDB
- `DEFAULT_AMENITIES`: Amenities mặc định cho Mitsui

## 🔄 Luồng xử lý (Processing Pipeline)

```
1. index.py: crawl_multi()
   ├─> Fetch URLs từ listing pages (1..NUM_PAGES)
   └─> Gọi crawl_pages() với danh sách URLs

2. custom_extractor_factory.py: setup_custom_extractor()
   ├─> Pre-hook: Clean HTML
   └─> Post-hooks (theo thứ tự):
       1. Extract images (exterior, floorplan, interior)
       2. Extract static info (tất cả thông tin cơ bản)
       3. Convert coordinates (XY → lat/lng)
       4. Set default amenities
       5. Process pricing (total_monthly, guarantor)
       6. Extract deposit/key info (cần total_monthly)
       7. Get district info (cần lat/lng)
       8. Cleanup temp fields (_html)

3. property_data_extractor.py: get_static_info()
   ├─> Chạy 13 extractors với safe error handling:
   │   ├─> header_info (building_name, floor_no, unit_no)
   │   ├─> available_from (ngày có thể vào ở)
   │   ├─> parking
   │   ├─> address_info (address, chome_banchi)
   │   ├─> rent_info (monthly_rent, monthly_maintenance)
   │   ├─> room_info (room_type, size)
   │   ├─> construction_date (year)
   │   ├─> structure_info (structure, floors)
   │   ├─> renewal_fee
   │   ├─> direction_info
   │   ├─> lock_exchange
   │   ├─> amenities
   │   └─> building_description
   └─> Return data với tất cả thông tin đã extract
```

### Dữ liệu đầu ra

Dữ liệu được lưu vào MongoDB collection `room_mitsui` với các trường:
- Thông tin cơ bản: tên, giá, diện tích, địa chỉ
- Tọa độ: `map_lat`, `map_lng`
- Hình ảnh: mảng URLs
- Tiện ích: mapping theo chuẩn hệ thống
- Thông tin ga tàu gần nhất

## Tính năng chính

1. **Multi-page crawling**: Crawl nhiều trang danh sách
2. **Data extraction**: Trích xuất đầy đủ thông tin property
3. **Image processing**: Lọc và tải hình ảnh chất lượng
4. **Coordinate conversion**: Chuyển đổi tọa độ XY sang lat/lng
5. **Station mapping**: Tìm ga tàu gần nhất
6. **Amenities mapping**: Mapping tiện ích sang chuẩn hệ thống

## Dependencies

- `requests`: HTTP requests
- `BeautifulSoup`: HTML parsing
- `app.jobs.crawl_single`: Base crawling functionality
- `app.utils`: Utility functions cho city/district/prefecture
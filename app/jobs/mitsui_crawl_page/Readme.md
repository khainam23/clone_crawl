# Mitsui Crawl Page

Module crawl dữ liệu bất động sản từ website Mitsui Chintai (https://www.mitsui-chintai.co.jp/).

## Mục đích

Crawl thông tin chi tiết các căn phòng cho thuê từ trang web Mitsui Chintai, bao gồm:
- Thông tin cơ bản (giá, diện tích, địa chỉ)
- Hình ảnh phòng
- Tiện ích và đặc điểm
- Tọa độ địa lý
- Thông tin ga tàu gần nhất

## Cấu trúc Module

```
mitsui_crawl_page/
├── index.py                    # Entry point chính
├── constants.py               # Cấu hình và mapping dữ liệu
├── property_data_extractor.py # Trích xuất dữ liệu property
├── html_processor.py          # Xử lý HTML
├── image_extractor.py         # Trích xuất hình ảnh
├── coordinate_converter.py    # Chuyển đổi tọa độ
├── station_service.py         # Lấy thông tin ga tàu
├── http_client.py            # HTTP client
└── custom_extractor_factory.py # Factory cho extractor
```

## Cách sử dụng

### Import và chạy crawl

```python
from app.jobs.mitsui_crawl_page.index import crawl_multi

# Chạy crawl multi-page
await crawl_multi()
```

### Cấu hình

Các cấu hình chính trong `constants.py`:
- `url_multi`: URL trang danh sách
- `item_selector`: CSS selector cho các item
- `batch_size`: Số lượng trang crawl mỗi lần
- `COLLECTION_NAME`: Tên collection MongoDB
- `MAX_IMAGES`: Số lượng ảnh tối đa

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
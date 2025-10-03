# Mitsui Crawl Page

Module crawl dữ liệu bất động sản từ website Mitsui Chintai (https://www.mitsui-chintai.co.jp/).

## Mục đích

Crawl thông tin chi tiết các căn phòng cho thuê từ Mitsui Chintai, bao gồm: giá, diện tích, địa chỉ, hình ảnh, tiện ích, tọa độ địa lý và ga tàu gần nhất.

## Cách sử dụng

```python
from app.jobs.mitsui_crawl_page.index import crawl_multi

# Chạy crawl
await crawl_multi()
```

**Cấu hình:** Chỉnh sửa `constants.py` để thay đổi URL, số trang crawl, collection MongoDB, v.v.

## Cấu trúc

```
mitsui_crawl_page/
├── index.py                      # Entry point - crawl URLs từ listing pages
├── constants.py                  # Cấu hình
├── property_data_extractor.py    # Trích xuất dữ liệu property
├── image_extractor.py            # Trích xuất hình ảnh
├── coordinate_converter.py       # Chuyển đổi tọa độ XY → lat/lng
└── custom_extractor_factory.py  # Factory tạo custom extractor
```

## Luồng xử lý

1. **index.py**: Fetch danh sách URLs từ listing pages
2. **custom_extractor_factory.py**: Setup pipeline xử lý (clean HTML → extract images → extract data → convert coordinates → process pricing → get district → cleanup)
3. **property_data_extractor.py**: Trích xuất 13 loại thông tin (tên, giá, địa chỉ, diện tích, tiện ích, v.v.)

## Dữ liệu đầu ra

Lưu vào MongoDB collection `room_mitsui` với các trường: tên, giá, diện tích, địa chỉ, tọa độ (`map_lat`, `map_lng`), hình ảnh, tiện ích, thông tin ga tàu.

## Tính năng

- Crawl nhiều trang danh sách
- Trích xuất đầy đủ thông tin property
- Xử lý và lọc hình ảnh
- Chuyển đổi tọa độ XY sang lat/lng
- Tìm ga tàu gần nhất
- Mapping tiện ích theo chuẩn hệ thống
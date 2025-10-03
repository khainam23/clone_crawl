# Tokyu Crawl Page

Module crawl dữ liệu bất động sản từ website Tokyu.

## Mục đích

Crawl thông tin chi tiết về các căn hộ cho thuê từ trang Tokyu, bao gồm:
- Thông tin tòa nhà (tên, loại, cấu trúc, địa chỉ, năm xây dựng)
- Thông tin căn hộ (số phòng, tầng, diện tích, hướng)
- Chi phí thuê (tiền thuê, phí quản lý, tiền đặt cọc, phí gia hạn)
- Tiện ích và chính sách thú cưng
- Hình ảnh và tọa độ bản đồ

## Cấu trúc

```
tokyu_crawl_page/
├── index.py                      # Entry point - chạy crawler
├── custom_extractor_factory.py  # Factory tạo extractors
├── property_data_extractor.py   # Logic trích xuất dữ liệu chính
├── image_extractor.py            # Trích xuất hình ảnh
├── map_extractor.py              # Trích xuất tọa độ bản đồ
└── constants.py                  # Cấu hình (URL, selectors, số trang)
```

## Cách sử dụng

```python
from app.jobs.tokyu_crawl_page.index import crawl_multi

# Chạy crawler
await crawl_multi()
```

## Cấu hình

Chỉnh sửa trong `constants.py`:
- `URL_MULTI`: URL trang danh sách
- `NUM_PAGES`: Số trang cần crawl
- `ITEM_SELECTOR`: CSS selector cho các item
- `DEFAULT_AMENITIES`: Giá trị mặc định cho tiện ích

## Quy trình xử lý

1. **Fetch URLs**: Lấy danh sách URL từ các trang listing
2. **Crawl từng trang**: Với mỗi URL, thực hiện 13 bước trích xuất:
   - Clean HTML
   - Trích xuất hình ảnh
   - Trích xuất thông tin tòa nhà
   - Trích xuất thông tin căn hộ
   - Trích xuất chi phí thuê
   - Trích xuất phí khác
   - Trích xuất mô tả
   - Trích xuất tiền đặt cọc & phí
   - Trích xuất tiện ích
   - Trích xuất chính sách thú cưng
   - Set giá trị mặc định
   - Tính toán thông tin tài chính
   - Trích xuất tọa độ bản đồ

## Tính năng nổi bật

- **Helper methods**: `_find_dt_dd()`, `_find_td()` để trích xuất HTML pattern phổ biến
- **Error handling**: Timeout 30s, xử lý lỗi từng trang, graceful degradation
- **Logging chi tiết**: Emoji indicators, progress tracking
- **Code sạch**: Giảm ~50+ dòng code nhờ helper methods

## Debug

Nếu gặp lỗi trích xuất:
1. Kiểm tra cấu trúc HTML có khớp với pattern không
2. Xác minh các label tiếng Nhật trong `_find_dt_dd()` và `_find_td()`
3. Xem logs để tìm bước extraction nào bị lỗi
4. Test từng extraction method với HTML mẫu

## Notes

- Tất cả extraction methods có signature: `(data: Dict, html: str) -> Dict`
- Thứ tự xử lý quan trọng (VD: phải extract rental costs trước khi tính deposits)
- Field `_html` tạm thời sẽ được cleanup ở cuối
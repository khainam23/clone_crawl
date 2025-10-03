# Crawl Structure - Generic Property Crawler

Module crawl thông tin chi tiết của từng property (bất động sản) từ URL cụ thể với hỗ trợ custom extractor.

## Mục đích

Crawl và extract dữ liệu chi tiết của một hoặc nhiều property từ danh sách URL, sau đó lưu vào MongoDB. Hỗ trợ custom extractor để xử lý các website khác nhau.

## Cấu trúc files

- `index.py` - Entry point chính, hàm `crawl_pages()` để crawl nhiều URLs
- `property_crawler.py` - Class `EnhancedPropertyCrawler` xử lý crawl logic
- `property_extractor.py` - Class `PropertyExtractor` extract dữ liệu từ HTML
- `custom_rules.py` - Hệ thống custom rules để xử lý các trường hợp đặc biệt

## Cách sử dụng

### Import và chạy cơ bản (không custom extractor)

```python
from app.jobs.crawl_strcture import crawl_pages

# Crawl danh sách URLs với basic extractor
urls = [
    "https://example.com/property/1",
    "https://example.com/property/2"
]

await crawl_pages(
    urls=urls,
    batch_size=5,           # Số lượng URLs crawl đồng thời
    id_mongo=123,           # ID để lưu vào MongoDB
    collection_name='properties'  # Tên collection MongoDB
)
```

### Sử dụng với custom extractor

```python
from app.jobs.crawl_strcture import crawl_pages
from app.jobs.mitsui_crawl_page.custom_extractor_factory import setup_custom_extractor

await crawl_pages(
    urls=urls,
    batch_size=5,
    id_mongo=123,
    collection_name='properties',
    custom_extractor_factory=setup_custom_extractor  # Custom extractor cho Mitsui
)
```

### Sử dụng trực tiếp crawler

```python
from app.jobs.crawl_strcture.property_crawler import EnhancedPropertyCrawler
from app.jobs.mitsui_crawl_page.custom_extractor_factory import setup_custom_extractor

# Với custom extractor
crawler = EnhancedPropertyCrawler(setup_custom_extractor)
results = await crawler.crawl_multiple_properties(urls, batch_size=5)

# Hoặc basic crawler
crawler = EnhancedPropertyCrawler()  # Không có custom extractor
results = await crawler.crawl_multiple_properties(urls, batch_size=5)
```

## Tính năng chính

- **Crawl đồng thời**: Hỗ trợ crawl nhiều URLs cùng lúc với batch_size
- **Extract toàn diện**: Lấy đầy đủ thông tin property theo PropertyModel
- **Custom rules**: Hệ thống rules linh hoạt xử lý các trường hợp đặc biệt
- **Validation**: Validate dữ liệu trước khi lưu
- **MongoDB integration**: Tự động lưu kết quả vào MongoDB
- **Logging**: Hiển thị progress và summary chi tiết

## Output

Kết quả crawl sẽ được lưu vào MongoDB với các thông tin:
- Thông tin cơ bản property (title, price, area, etc.)
- Hình ảnh (tách thành các field riêng biệt)
- Thông tin giao thông (stations)
- Metadata crawl (timestamp, source URL)
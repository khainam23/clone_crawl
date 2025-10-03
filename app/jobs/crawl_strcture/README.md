# Crawl Structure

Module crawl thông tin chi tiết của property (bất động sản) từ URL và lưu vào MongoDB.

## Mục đích

Crawl dữ liệu chi tiết từ danh sách URL property, hỗ trợ custom extractor cho từng website khác nhau.

## Cách sử dụng

### 1. Crawl cơ bản

```python
from app.jobs.crawl_strcture import crawl_pages

urls = [
    "https://example.com/property/1",
    "https://example.com/property/2"
]

await crawl_pages(
    urls=urls,
    batch_size=5,                    # Số URL crawl đồng thời
    id_mongo=123,                    # ID bắt đầu trong MongoDB
    collection_name='properties'     # Tên collection
)
```

### 2. Crawl với custom extractor

```python
from app.jobs.crawl_strcture import crawl_pages
from app.jobs.mitsui_crawl_page.custom_extractor_factory import setup_custom_extractor

await crawl_pages(
    urls=urls,
    batch_size=5,
    id_mongo=123,
    collection_name='properties',
    custom_extractor_factory=setup_custom_extractor  # Custom cho website cụ thể
)
```

### 3. Sử dụng crawler trực tiếp

```python
from app.jobs.crawl_strcture.property_crawler import EnhancedPropertyCrawler

crawler = EnhancedPropertyCrawler()  # Hoặc truyền custom_extractor_factory
results = await crawler.crawl_multiple_properties(urls, batch_size=5)
```

## Tính năng

- ✅ Crawl đồng thời nhiều URL (batch processing)
- ✅ Tự động lưu vào MongoDB sau mỗi batch
- ✅ Hỗ trợ custom extractor cho từng website
- ✅ Validate dữ liệu trước khi lưu
- ✅ Logging chi tiết progress và summary

## Cấu trúc

```
crawl_strcture/
├── index.py                 # Entry point - hàm crawl_pages()
├── property_crawler.py      # Logic crawl chính
├── property_extractor.py    # Extract dữ liệu từ HTML
├── custom_rules.py          # Hệ thống custom rules
└── crawler_pool.py          # Quản lý pool crawlers
```

## Output

Dữ liệu được lưu vào MongoDB bao gồm:
- Thông tin property (title, price, area, ...)
- Hình ảnh
- Thông tin giao thông (stations)
- Metadata (timestamp, source URL)
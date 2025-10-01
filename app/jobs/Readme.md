# Jobs Module

Module quản lý các job crawl dữ liệu bất động sản từ các trang web khác nhau.

## Mục đích

- Quản lý và đăng ký các job crawl tự động
- Cung cấp cấu trúc chuẩn để tạo job crawl cho trang web mới
- Hỗ trợ scheduler để chạy job theo lịch

## Cấu trúc thư mục

```
jobs/
├── index.py                    # Registry quản lý job
├── __init__.py                # Import và đăng ký job
├── print_job.py               # Job mẫu để test
├── mitsui_job.py              # Job crawl Mitsui
├── mitsui_crawl_page/         # Module crawl Mitsui
├── tokyu_crawl_page/          # Module crawl Tokyu
└── crawl_strcture/            # Cấu trúc base cho crawl
```

## Cách sử dụng

### 1. Tạo job crawl mới

Để tạo job cho trang web mới, làm theo các bước:

1. **Tạo thư mục crawl**: `{tên_trang}_crawl_page/`
2. **Tạo file job**: `{tên_trang}_job.py`
3. **Đăng ký job** trong `__init__.py`

### 2. Cấu trúc file job

```python
# example_job.py
from app.jobs.index import job_registry

async def crawl_example():
    # Logic crawl ở đây
    return {"status": "success", "message": "Crawl completed"}

# Cấu hình job
job_config = {
    'func': crawl_example,
    'trigger': 'cron',
    'seconds': 60,
    'id': 'crawl_example_job',
    'replace_existing': True
}

# Đăng ký job
job_registry.register(job_config)
```

### 3. Đăng ký job trong __init__.py

```python
# Thêm import job mới
from . import example_job
```

## Thứ tự crawl khuyến nghị

1. **Crawl ảnh trước** - Tải và xử lý hình ảnh
2. **Thông tin cố định** - Dữ liệu không thay đổi (địa chỉ, diện tích)
3. **Thông tin biến đổi** - Giá cả, trạng thái
4. **Thông tin bổ sung** - Tiện ích, mô tả

## File quan trọng

- **`index.py`**: Registry quản lý tất cả job
- **`print_job.py`**: Job mẫu để test scheduler
- **`__init__.py`**: Import và đăng ký job (⚠️ Bắt buộc import job mới ở đây)

## Ví dụ job có sẵn

- **`mitsui_job.py`**: Crawl dữ liệu từ Mitsui Chintai
- **`print_job.py`**: Job test in thông báo 


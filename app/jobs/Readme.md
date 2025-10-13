# Jobs Module

Module quản lý các job crawl dữ liệu bất động sản tự động theo lịch.

## Mục đích

Cung cấp hệ thống đăng ký và quản lý job crawl cho các trang web bất động sản khác nhau.

## Cấu trúc

```
jobs/
├── index.py                    # Registry quản lý job
├── __init__.py                 # Đăng ký tất cả job
├── print_job.py                # Job test mẫu
├── mitsui_job.py               # Job crawl Mitsui
├── tokyu_job.py                # Job crawl Tokyu
├── mitsui_crawl_page/          # Module crawl Mitsui
├── tokyu_crawl_page/           # Module crawl Tokyu
└── crawl_strcture/             # Base structure cho crawl
```

## Cách thêm job mới

### Bước 1: Tạo file job

Tạo file `{tên_trang}_job.py`:

```python
from app.jobs.index import job_registry

async def crawl_example():
    """Logic crawl của bạn"""
    # TODO: Implement crawl logic
    return {"status": "success"}

# Đăng ký job
job_registry.register({
    'func': crawl_example,
    'trigger': 'cron',
    'seconds': 60,                    # Chạy mỗi 60 giây
    'id': 'crawl_example_job',
    'replace_existing': True
})
```

### Bước 2: Import job trong `__init__.py`

```python
from . import example_job  # Thêm dòng này
```

### Bước 3: Tạo module crawl (tùy chọn)

Nếu logic phức tạp, tạo folder `{tên_trang}_crawl_page/` để tổ chức code.

## Trigger options

- `'cron'` + `seconds`: Chạy định kỳ theo giây
- `'cron'` + `hour`, `minute`: Chạy vào giờ cụ thể
- `'interval'` + `seconds`: Chạy lặp lại sau mỗi khoảng thời gian

## Ví dụ có sẵn

- **`print_job.py`**: Job test đơn giản
- **`mitsui_job.py`**: Crawl Mitsui Chintai
- **`tokyu_job.py`**: Crawl Tokyu

## Lưu ý

- Job phải là async function
- Mỗi job cần `id` duy nhất
- Nhớ import job mới trong `__init__.py` để job được đăng ký
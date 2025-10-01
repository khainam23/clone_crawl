# Arealty Crawler API
## 🚀 Tính năng chính

- **RESTful API**: Được xây dựng với FastAPI, cung cấp API documentation tự động
- **Crawler tự động**: Sử dụng APScheduler để lên lịch thu thập dữ liệu định kỳ
- **Database MongoDB**: Lưu trữ dữ liệu bất động sản với Motor (async MongoDB driver)
- **Async/Await**: Hỗ trợ xử lý bất đồng bộ cho hiệu suất cao
- **Health Check**: Endpoint kiểm tra tình trạng hoạt động của ứng dụng
- **Environment Configuration**: Quản lý cấu hình thông qua file .env

## 📋 Yêu cầu hệ thống

- Python 3.8+
- MongoDB
- Virtual Environment (khuyến nghị)

## 🛠️ Cài đặt

### 1. Clone repository

```bash
git clone <repository-url>
cd arealty_craw_public
```

### 2. Tạo và kích hoạt virtual environment

```bash
python -m venv .venv

# Windows
.venv\Scripts\activate

# Linux/Mac
source .venv/bin/activate
```

### 3. Cài đặt dependencies

```bash
pip install -r requirements.txt
```

### 4. Cấu hình environment

Coppy file .env.example ra một file .env và chỉnh sửa các giá trị theo nhu cầu.

`coppy .env.example .env`

## 🚀 Chạy ứng dụng

### Development mode

```bash
python run.py
```

### Production mode với Gunicorn

```bash
gunicorn run:app -w 4 -k uvicorn.workers.UvicornWorker --bind 127.0.0.1:8000
```

### Sử dụng Uvicorn trực tiếp

```bash
uvicorn run:app --host 127.0.0.1 --port 8000 --reload
```

## 📁 Cấu trúc dự án

```
arealty_craw_public/
├── app/
│   ├── core/
│   │   ├── config.py          # Cấu hình ứng dụng
│   │   ├── scheduler.py       # Quản lý scheduler
│   │   └── __init__.py
│   ├── db/
│   │   ├── mongodb.py         # Kết nối MongoDB
│   │   └── __init__.py
│   ├── docs/
│   │   ├── Readme.md          # Tài liệu bổ sung
│   │   └── structure.json     # Cấu trúc dữ liệu tham khảo
│   ├── jobs/
│   │   ├── print_job.py       # Job mẫu
│   │   ├── register_jobs.py   # Đăng ký các job
│   │   └── __init__.py
│   ├── models/
│   │   ├── data_model.py      # Models dữ liệu
│   │   └── __init__.py
│   ├── routes/
│   │   ├── health.py          # Health check endpoint
│   │   └── __init__.py
│   ├── main.py                # FastAPI application
│   └── __init__.py
├── .env                       # Environment variables
├── .gitignore
├── requirements.txt           # Python dependencies
├── run.py                     # Application entrypoint
└── Readme.md
```

## 🔌 API Endpoints

### Health Check

```http
GET /api/v1/health
```

Kiểm tra tình trạng hoạt động của ứng dụng.

**Response:**
```json
{
  "status": "healthy",
  "timestamp": "2024-01-01T00:00:00Z"
}
```

### API Documentation

Khi ứng dụng đang chạy, bạn có thể truy cập:

- **Swagger UI**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`

## 🔧 Cấu hình

Tất cả cấu hình được quản lý thông qua file `.env` và class `Settings` trong `app/core/config.py`.

### Các biến môi trường chính:

| Biến | Mô tả | Giá trị mặc định |
|------|-------|------------------|
| `MONGODB_URL` | URL kết nối MongoDB | `mongodb://localhost:27017` |
| `DATABASE_NAME` | Tên database | `arealty_crawler` |
| `API_HOST` | Host API | `0.0.0.0` |
| `API_PORT` | Port API | `8000` |
| `DEBUG` | Chế độ debug | `false` |
| `SCHEDULER_TIMEZONE` | Timezone cho scheduler | `UTC` |
| `CRAWLER_USER_AGENT` | User agent cho crawler | Mozilla/5.0... |
| `CRAWLER_DELAY` | Delay giữa các request | `1.0` |

## 📊 Scheduler Jobs

Ứng dụng sử dụng APScheduler để chạy các job định kỳ. Các job được đăng ký trong `app/jobs/register_jobs.py`.

## 🗄️ Database

Ứng dụng sử dụng MongoDB với Motor driver để hỗ trợ async operations. Kết nối database được quản lý trong `app/db/mongodb.py`.

## 🧪 Testing

```bash
# Chạy tests
pytest

# Chạy tests với coverage
pytest --cov=app
```

## 🔍 Code Quality

Dự án sử dụng các công cụ sau để đảm bảo chất lượng code:

```bash
# Format code với Black
black .

# Kiểm tra code style với Flake8
flake8 .
```

## 📝 Development

### Thêm endpoint mới

1. Tạo router trong `app/routes/`
2. Import và include router trong `app/main.py`

### Thêm job mới

1. Tạo job function trong `app/jobs/`
2. Đăng ký job trong `app/jobs/register_jobs.py`

### Thêm model mới

1. Tạo model trong `app/models/`
2. Import model nơi cần sử dụng
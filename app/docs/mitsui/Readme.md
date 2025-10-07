# Mitsui Crawler - Hướng dẫn xử lý dữ liệu

## 📋 Tổng quan

Crawler này xử lý dữ liệu từ website Mitsui với một số đặc thù cần lưu ý cách xử lý.

---

## ⚠️ Các vấn đề cần xử lý

### 1. Dữ liệu không chuẩn

- Một số phần thông tin nằm không theo format thông thường
- Cần xử lý và chuẩn hóa dữ liệu trước khi lưu

### 2. Giá trị mặc định

- Có vài giá trị cần set mặc định khi dữ liệu bị thiếu
- Cần định nghĩa các giá trị fallback phù hợp
- Có các trường cần setup cố định như:

```python
{
    'credit_card': 'Y',         # Credit Card Accepted
    'no_guarantor': 'Y',        # No Guarantor
    'aircon': 'Y',              # Aircon
    'aircon_heater': 'Y',       # Aircon Heater
    'bs': 'Y',                  # Broadcast Satellite TV
    'cable': 'Y',               # Cable
    'internet_broadband': 'Y',  # Broadband
    'internet_wifi': 'Y',       # Internet WiFi
    'phoneline': 'Y',           # Phoneline
    'flooring': 'Y',            # Flooring
    'system_kitchen': 'Y',      # System Kitchen
    'bath': 'Y',                # Bath
    'shower': 'Y',              # Shower
    'unit_bath': 'Y',           # Unit Bath
    'western_toilet': 'Y',      # Western Toilet
    'insurance': 20000          # Insurance
}
```

### 3. Tính toán giá tiền

- Một vài trường tiền cần tính toán theo công thức riêng
- Không sử dụng trực tiếp giá trị từ source
- **Chỉ dùng cho tính toán**: `total_monthly` (int) - Lưu lại tổng `monthly_rent + monthly_maintenance` + `other_subscription_fees` - nếu other_subscription_fees < 0 thì đặt nó là 0
- **Guarantor Min** = `total_monthly * 0.5`
- **Guarantor Max** = `total_monthly * 0.8`

### 4. Chuyển đổi ngày tháng

Xử lý các format ngày tháng đặc biệt:

| Input | Output |
|-------|--------|
| `即可` | Ngày hôm nay |
| `上旬` | Ngày 5 của tháng |
| `中旬` | Ngày 15 của tháng |
| `下旬` | Ngày 25 của tháng |
| `月末` | Ngày cuối tháng |

**Các định dạng được hỗ trợ:**
- `YYYY年MM月DD日`
- `MM月DD日` (ngầm định năm hiện tại)
- `YYYY/MM/DD`
- `MM/DD` (ngầm định năm hiện tại)

**Kết quả:** Lưu vào `data["available_from"]` dưới dạng ISO date (`YYYY-MM-DD`)

### 5. Xử lý checkbox Parking

**Quy trình:**
1. Tìm thẻ `<dt>駐車場</dt>` và lấy nội dung `<dd>` liền kề
2. Làm sạch HTML để lấy text
3. Kiểm tra giá trị:
   - **Giá trị phủ định** (`なし`, `無し`, `×`, `不可`, `無`, `NO`, ...) → `parking = 'N'`
   - **Các trường hợp khác** → `parking = 'Y'` (mặc định)
   - **Lỗi xử lý** → `parking = 'Y'`

**Kết quả:**
- `"Y"` = Có/được phép đỗ xe
- `"N"` = Không có/không được phép đỗ xe

### 6. Chuyển đổi tọa độ

- Trong trang sẽ có một link tới gg, tuy nhiên đơn giản sẽ dùng link gg này `https://www.google.co.jp/maps/place/{encoded_address}` sau đó chờ để xuất ra tọa độ dựa vào `@lap,lat`

### 7. Xử lý địa chỉ

- **Thêm trường mới**: `address` (string) - Lưu địa chỉ đầy đủ của bất động sản
- Cần xử lý và làm sạch dữ liệu địa chỉ từ source

### 8. Xử lý structure

- Structure phải được xử lý theo định dạng chuẩn của dự án chính
- Sử dụng mapping để chuyển đổi từ tiếng Nhật sang mã chuẩn

**Structure Mapping:**

```python
STRUCTURE_MAPPING = {
    "木造": "wood",                              # Gỗ
    "ブロック": "cb",                            # Block/Concrete Block
    "鉄骨造": "steel_frame",                     # Khung thép
    "鉄筋コンクリート（RC）": "rc",               # Beton cốt thép
    "鉄骨鉄筋コンクリート（SRC）": "src",         # Thép beton cốt thép
    "プレキャストコンクリート（PC）": "pc",       # Beton đúc sẵn
    "鉄骨プレキャスト（HPC）": "other",           # Thép beton đúc sẵn
    "軽量鉄骨": "light_gauge_steel",             # Thép nhẹ
    "軽量気泡コンクリート（ALC）": "alc",         # Beton xốp nhẹ
    "その他": "other",                           # Khác
}
```

**Quy trình xử lý:**
1. Lấy giá trị structure từ source (tiếng Nhật)
2. Tra cứu trong `STRUCTURE_MAPPING` bằng cách tính độ diff > 50% thì lấy (lấy cao nhất)
3. Nếu không tìm thấy → gán giá trị `"other"`
4. Lưu kết quả vào `data["structure"]`

### 9. Xử lý thông tin về địa lý

**API Endpoint:**
```
https://bmatehouse.com/api/routes/get_by_position
```

**Quy trình xử lý:**
1. **Crawl thông tin địa chỉ** từ API endpoint trên
2. **Lấy prefecture_id và city_id** từ response
3. **Gọi service** để lấy thông tin chi tiết phù hợp
4. **Lấy service district** để lấy tên district

**Kết quả cần lưu:**
- `prefecture_id` (int) - ID tỉnh/thành phố
- `city_id` (int) - ID quận/huyện  
- `district_name` (string) - Tên district từ service 

---

## 🖼️ Quy tắc crawl ảnh

### Biến quan trọng trong JavaScript

- **`RF_firstfloorplan_photo`**: Link trực tiếp của ảnh floor plan
- **`RF_gallery_url`**: Chứa JSON array các ảnh về căn phòng

### Format JSON ảnh

```json
[
  {
    "part": "002",
    "ROOM_NO": 99999,
    "name": "10476a02.jpg",
    "UPD_DATE": "2024-02-08 18:00:18",
    "filename": "https://mfhl.mitsui-chintai.co.jp/websearch/image/10476/10476a02.jpg",
    "onerror": "https://www.mitsui-chintai.co.jp/rf/photo/10476/10476a02.jpg/register"
  }
]
```

### Phân loại ảnh theo ROOM_NO

| ROOM_NO | Loại ảnh | Mô tả |
|---------|----------|-------|
| `99999` | Building images | Ảnh thuộc về tòa nhà |
| `[số phòng]` | Room images | Ảnh thuộc về phòng cụ thể |

> ⚠️ **Lưu ý**: Ảnh phòng có thể bao gồm cả floor plan, cần loại bỏ nếu không cần thiết

### Quy trình xử lý ảnh

1. **Gọi API** từ `RF_gallery_url`
2. **Phân loại ảnh** dựa trên `ROOM_NO`
3. **Lọc bỏ ảnh trùng lặp** (nếu có)
4. **Download và lưu ảnh** theo cấu trúc thư mục phù hợp

---

## 📚 Crawl nhiều trang

### URL Template
```
https://www.mitsui-chintai.co.jp/rf/result?page=x
```

### Quy trình xử lý
- Sử dụng parameter `page=x` với vòng lặp `for`
- Chỉ định batch xử lý trong một lần để tăng tốc độ
- **Lưu ý**: Cần kiểm soát thời gian chờ page load để tránh timeout

### Khuyến nghị
- Xử lý nhiều trang song song sẽ nhanh hơn
- Cần cân bằng giữa tốc độ và độ ổn định
- Monitor memory usage khi xử lý batch lớn

---

## 📝 Ghi chú

- Tất cả các xử lý đặc biệt cần được test kỹ lưỡng
- Cần backup dữ liệu trước khi áp dụng các thay đổi lớn
- Theo dõi log để phát hiện các trường hợp edge case
- Kiểm tra performance khi crawl số lượng lớn
- Đảm bảo tuân thủ robots.txt và rate limiting
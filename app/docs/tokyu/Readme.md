# Tokyu Crawler - Hướng dẫn xử lý dữ liệu

## 📋 Tổng quan

Crawler này xử lý dữ liệu từ website Tokyu với các quy tắc xử lý đặc thù về ảnh, giá trị và tính toán.

---

## ⚠️ Các vấn đề cần xử lý

### 1. Xử lý giá trị rỗng

- Các giá trị có dấu `-` nghĩa là số `0`
- **Quan trọng**: Vẫn phải giữ lại field, không được bỏ qua
- Chuyển đổi `-` thành `0` khi lưu vào database

### 2. Tính toán giá tiền

**Các công thức tính toán:**

| Trường | Công thức | Mô tả |
|--------|-----------|-------|
| **Guarantor Min** | `total_monthly * 0.5` | 50% tổng phí hàng tháng |
| **Guarantor Max** | `total_monthly * 1.0` | 100% tổng phí hàng tháng |
| **Agency Fee** | `monthly_rent * 1.1` | 110% tiền thuê hàng tháng |

**Lưu ý:**
- `total_monthly` = `monthly_rent + monthly_maintenance`
- Kết quả làm tròn theo quy tắc của dự án

### 3. Mapping tên trường

- Một số trường có tên khác so với tên được gợi ý trong schema
- Cần kiểm tra và mapping chính xác từ source sang database schema
- Tham khảo mapping table trong code để đảm bảo tính nhất quán

---

## 🖼️ Quy tắc crawl ảnh

### Quy trình xử lý ảnh

**Bước 1: Lấy link trang ảnh**
- Tìm thẻ `li.print_album > a`
- Lấy giá trị `href` để truy cập vào trang chi tiết ảnh

**Bước 2: Phân loại và crawl ảnh**

Sau khi truy cập vào trang chi tiết, crawl ảnh theo các selector sau:

| Loại ảnh | CSS Selector | Mô tả |
|----------|--------------|-------|
| **Floor Plan** | `div#room_photo_album > * > ul.clearFix > li:first > img` | Ảnh mặt bằng phòng |
| **Exterior** | `div#mansion_img_album > * > ul > li:first > img` | Ảnh bên ngoài tòa nhà |
| **Interior** | `div#common_area_album > * > ul > li > img` | Ảnh khu vực chung/nội thất |

**Lưu ý:**
- Chỉ lấy ảnh đầu tiên (`li:first`) cho Floor Plan và Exterior
- Lấy tất cả ảnh (`li`) cho Interior
- Kiểm tra ảnh có tồn tại trước khi download
- Xử lý lỗi khi ảnh không load được

---

## 📝 Ghi chú

- Kiểm tra kỹ các selector CSS trước khi chạy crawler
- Xử lý timeout khi load trang ảnh
- Theo dõi log để phát hiện các trường hợp lỗi
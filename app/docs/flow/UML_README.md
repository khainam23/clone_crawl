# UML Diagrams - Arealty Crawler

Thư mục này chứa các sơ đồ UML mô tả kiến trúc và luồng hoạt động của hệ thống Arealty Crawler.

## 📊 Các file UML

### 1. **workflow.puml** - Sơ đồ luồng hoạt động (Activity Diagram)
Mô tả chi tiết luồng hoạt động của toàn bộ hệ thống từ khi khởi động đến khi tắt.

**Nội dung chính:**
- Khởi động ứng dụng (run.py → FastAPI → MongoDB → Scheduler)
- Đăng ký và quản lý Jobs
- API Server endpoints
- Luồng thực thi Job Mitsui (crawl → extract → save)
- Luồng thực thi Job Tokyu (crawl → extract → save)
- Tắt ứng dụng

**Phù hợp cho:** Hiểu tổng quan luồng xử lý và các bước thực thi

---

### 2. **architecture.puml** - Sơ đồ kiến trúc (Component Diagram)
Mô tả kiến trúc tổng thể của hệ thống, các thành phần và mối quan hệ giữa chúng.

**Nội dung chính:**
- **Core Layer:** FastAPI, Config, Scheduler
- **Database Layer:** MongoDB với các collections
- **API Routes:** Health check endpoints
- **Jobs Layer:** Mitsui Job, Tokyu Job, Crawl Structure
- **Services Layer:** Station Service
- **Utils Layer:** Các utility functions
- **Models Layer:** Data models
- **External Libraries:** Crawl4AI, BeautifulSoup, Requests, Pydantic

**Phù hợp cho:** Hiểu cấu trúc code và dependencies giữa các module

---

### 3. **sequence.puml** - Sơ đồ tuần tự (Sequence Diagram)
Mô tả chi tiết luồng xử lý của một crawler job từ đầu đến cuối.

**Nội dung chính:**
- Scheduler trigger job
- Xóa dữ liệu cũ trong collection
- Thu thập danh sách URLs từ trang listing
- Crawl chi tiết từng property (batch processing)
- Trích xuất dữ liệu (property, location, images, coordinates, amenities)
- Validate và transform data
- Lưu kết quả vào MongoDB
- Log và hoàn thành job

**Phù hợp cho:** Hiểu chi tiết từng bước xử lý và tương tác giữa các components

---

## 🛠️ Cách xem UML Diagrams

### Phương pháp 1: Visual Studio Code (Khuyến nghị)
1. Cài đặt extension **PlantUML**:
   - Mở VS Code
   - Vào Extensions (Ctrl+Shift+X)
   - Tìm "PlantUML" và cài đặt

2. Cài đặt Java (nếu chưa có):
   - PlantUML cần Java để render
   - Download từ: https://www.java.com/download/

3. Xem diagram:
   - Mở file `.puml`
   - Nhấn `Alt+D` để preview
   - Hoặc click chuột phải → "Preview Current Diagram"

### Phương pháp 2: Online PlantUML Editor
1. Truy cập: http://www.plantuml.com/plantuml/uml/
2. Copy nội dung file `.puml`
3. Paste vào editor
4. Xem kết quả render

### Phương pháp 3: PlantUML Server (Local)
```bash
# Sử dụng Docker
docker run -d -p 8080:8080 plantuml/plantuml-server:jetty

# Truy cập: http://localhost:8080
```

### Phương pháp 4: Export sang hình ảnh
Với VS Code + PlantUML extension:
- Mở file `.puml`
- Nhấn `Ctrl+Shift+P`
- Chọn "PlantUML: Export Current Diagram"
- Chọn format: PNG, SVG, PDF, etc.

---

## 📖 Cách đọc các sơ đồ

### Activity Diagram (workflow.puml)
- **Hình chữ nhật bo góc:** Hoạt động/Action
- **Hình thoi:** Điều kiện/Decision
- **Mũi tên:** Luồng thực thi
- **Fork/Join:** Xử lý song song
- **Partition:** Nhóm các hoạt động liên quan
- **Note:** Ghi chú bổ sung

### Component Diagram (architecture.puml)
- **Component [...]:** Thành phần của hệ thống
- **Package {...}:** Nhóm các components
- **Database:** Cơ sở dữ liệu
- **Mũi tên -->:** Quan hệ phụ thuộc/sử dụng
- **Note:** Ghi chú về chức năng

### Sequence Diagram (sequence.puml)
- **Actor/Participant:** Các đối tượng tham gia
- **Mũi tên -->:** Message/Call
- **Activate/Deactivate:** Thời gian xử lý
- **Loop:** Vòng lặp
- **Par:** Xử lý song song
- **Note:** Ghi chú về logic

---

## 🎨 Màu sắc trong diagrams

| Màu | Ý nghĩa |
|-----|---------|
| 🔵 Light Blue | Khởi động/Tắt ứng dụng, Entry points |
| 🟢 Light Green | Core components, Đăng ký jobs |
| 🔴 Light Coral | Database, API Server |
| 🟡 Light Yellow | Job execution, Routes |
| 🟣 Light Pink | Jobs layer |
| 🔷 Lavender | Services |
| 🔶 Light Cyan | Utils |

---

## 📝 Cập nhật UML Diagrams

Khi có thay đổi trong code, cần cập nhật các file UML tương ứng:

1. **Thêm job mới:** Cập nhật cả 3 files
   - `workflow.puml`: Thêm luồng job mới
   - `architecture.puml`: Thêm component job mới
   - `sequence.puml`: Có thể tạo sequence riêng nếu logic khác biệt

2. **Thêm endpoint mới:** Cập nhật
   - `workflow.puml`: Thêm vào phần API Server
   - `architecture.puml`: Thêm vào API Routes

3. **Thêm utility/service mới:** Cập nhật
   - `architecture.puml`: Thêm vào Utils/Services Layer
   - `sequence.puml`: Nếu được sử dụng trong luồng chính

4. **Thay đổi database:** Cập nhật
   - `workflow.puml`: Cập nhật phần lưu trữ
   - `architecture.puml`: Cập nhật Database Layer
   - `sequence.puml`: Cập nhật phần tương tác với MongoDB

---

## 🔗 Tài liệu tham khảo

- **PlantUML Official:** https://plantuml.com/
- **PlantUML Activity Diagram:** https://plantuml.com/activity-diagram-beta
- **PlantUML Component Diagram:** https://plantuml.com/component-diagram
- **PlantUML Sequence Diagram:** https://plantuml.com/sequence-diagram
- **PlantUML Cheat Sheet:** https://ogom.github.io/draw_uml/plantuml/

---

## 💡 Tips

1. **Xem nhanh:** Sử dụng VS Code với PlantUML extension để xem real-time preview
2. **Export:** Export sang PNG/SVG để chia sẻ hoặc đưa vào documentation
3. **Version control:** Các file `.puml` là text nên dễ dàng track changes với Git
4. **Customize:** Có thể thay đổi theme, màu sắc, font trong file `.puml`
5. **Split diagrams:** Nếu diagram quá phức tạp, nên tách thành nhiều file nhỏ hơn

---

## 📧 Liên hệ

Nếu có thắc mắc về các UML diagrams, vui lòng liên hệ team development.
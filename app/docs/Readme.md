# Tài liệu hệ thống

## structure.json: Cấu trúc tham khảo cho output

File `structure.json` định nghĩa cấu trúc dữ liệu đầy đủ cho hệ thống bất động sản, bao gồm 217 trường dữ liệu được phân loại như sau:

### 1. Thông tin cơ bản
- **Định danh**: `link`, `property_csv_id`
- **Địa chỉ**: `postcode`, `prefecture`, `city`, `district`, `chome_banchi`
- **Vị trí**: `map_lat`, `map_lng`

### 2. Thông tin tòa nhà
- **Cơ bản**: `building_type`, `year`, `num_units`, `floors`, `basement_floors`, `structure`, `building_style`
- **Tên tòa nhà** (đa ngôn ngữ): `building_name_en/ja/zh_CN/zh_TW`
- **Mô tả tòa nhà** (đa ngôn ngữ): `building_description_en/ja/zh_CN/zh_TW`
- **Địa danh gần đó** (đa ngôn ngữ): `building_landmarks_en/ja/zh_CN/zh_TW`

### 3. Giao thông công cộng
Thông tin cho 5 ga tàu gần nhất, mỗi ga bao gồm:
- Tên ga: `station_name_1` đến `station_name_5`
- Tuyến tàu: `train_line_name_1` đến `train_line_name_5`
- Thời gian di chuyển: `walk_`, `bus_`, `car_`, `cycle_` (1-5)

### 4. Tiện ích tòa nhà
- **Đậu xe**: `parking`, `parking_cost`, `bicycle_parking`, `motorcycle_parking`
- **Tiện nghi**: `autolock`, `elevator`, `concierge`, `delivery_box`, `gym`, `swimming_pool`
- **Chính sách**: `credit_card`, `newly_built`, `pets`, `ur`

### 5. Thông tin căn hộ
- **Cơ bản**: `room_type`, `size`, `unit_no`, `floor_no`, `balcony_size`
- **Hướng nhà**: `facing_north/northeast/east/southeast/south/southwest/west/northwest`
- **Mô tả** (đa ngôn ngữ): `property_description_en/ja/zh_CN/zh_TW`

### 6. Chi phí và điều khoản thuê
- **Tiền thuê**: `monthly_rent`, `monthly_maintenance`
- **Phí ban đầu**: `months_deposit`, `numeric_deposit`, `months_key`, `numeric_key`
- **Phí khác**: `months_guarantor`, `numeric_guarantor`, `months_agency`, `numeric_agency`
- **Phí bổ sung**: `lock_exchange`, `fire_insurance`, `other_initial_fees`, `other_subscription_fees`
- **Điều khoản**: `lease_date`, `lease_months`, `lease_type`, `rent_negotiable`

### 7. Tiện nghi căn hộ
- **Điều hòa**: `aircon`, `aircon_heater`, `underfloor_heating`
- **Bếp**: `full_kitchen`, `system_kitchen`, `counter_kitchen`, `induction_cooker`, `range`, `microwave`, `oven`
- **Phòng tắm**: `bath`, `shower`, `unit_bath`, `auto_fill_bath`, `bath_water_heater`
- **Toilet**: `japanese_toilet`, `western_toilet`, `washlet`, `separate_toilet`
- **Thiết bị**: `refrigerator`, `washing_machine`, `washer_dryer`, `dishwasher`
- **Nội thất**: `furnished`, `carpet`, `flooring`, `tatami`, `blinds`, `drapes`
- **Kết nối**: `internet_broadband`, `internet_wifi`, `phoneline`, `cable`, `bs`

### 8. Media và hình ảnh
- **Video**: `youtube`, `vr_link`
- **Hình ảnh**: 16 cặp `image_category_` và `image_url_` (1-16)

### 9. Thông tin quản lý
- **Quảng cáo**: `ad_type`, `available_from`, `featured_a/b/c`
- **Hệ thống**: `create_date`, `discount`, `numeric_guarantor_max`

Tất cả các trường boolean sử dụng định dạng 'Y'/'N'. Các trường đa ngôn ngữ hỗ trợ tiếng Anh (en), tiếng Nhật (ja), tiếng Trung giản thể (zh_CN) và tiếng Trung phồn thể (zh_TW).
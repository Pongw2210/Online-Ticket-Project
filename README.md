# 🎫 TicketBox Clone - Hệ thống đặt vé sự kiện trực tuyến

## 📋 Mô tả
TicketBox Clone là một hệ thống đặt vé sự kiện trực tuyến được xây dựng bằng Flask.

Ứng dụng cho phép:

Người dùng đăng ký/đăng nhập, tìm kiếm, mua vé và chọn ghế ngồi.

Người tổ chức sự kiện có thể đăng tải và quản lý sự kiện.

Thanh toán nhanh chóng bằng QR code với nhiều phương thức.

Dự án được thiết kế theo mô hình MVC (Model–View–Controller), dễ bảo trì và mở rộng.

## 🚀 Cách chạy ứng dụng

### 1. Cài đặt dependencies
```bash
pip install flask flask-sqlalchemy pymysql qrcode[pil] cloudinary
```

### 2. Cấu hình database
- Đảm bảo MySQL server đang chạy
- Tạo database `ticket_db` với charset `utf8mb4`
- Cập nhật thông tin kết nối trong `app/__init__.py` nếu cần

### 3. Khởi tạo database
```bash
python -m app.data.create_db
```

### 4. Chạy ứng dụng
Có 2 cách:

**Cách 1: Sử dụng file run.py ở thư mục gốc**
```bash
python run.py
```

**Cách 2: Sử dụng module app**
```bash
python -m app.run
```

### 5. Truy cập ứng dụng
Mở trình duyệt và truy cập: `http://localhost:5000`

## 🔐 Tính năng chính

### Authentication
- ✅ Đăng ký tài khoản mới với email
- ✅ Kiểm tra email hợp lệ khi đăng ký
- ✅ Đăng nhập/đăng xuất
- ✅ Session-based authentication
- ✅ Bảo vệ các trang nhạy cảm

### Sự kiện
- ✅ Xem danh sách sự kiện
- ✅ Tìm kiếm sự kiện
- ✅ Xem chi tiết sự kiện
- ✅ Tạo sự kiện mới (cho người tổ chức)

### Đặt vé
- ✅ Chọn loại vé và số lượng
- ✅ Chọn ghế ngồi
- ✅ Thanh toán với QR code
- ✅ Xem vé đã mua

### QR Code
- ✅ Tạo QR code cho thanh toán
- ✅ Tạo QR code cho vé đã mua
- ✅ Hỗ trợ nhiều phương thức thanh toán

## 🏗️ Cấu trúc project

```
OnlineTicketProject/
├── app/
│   ├── __init__.py          # Flask app factory
│   ├── run.py               # App runner
│   ├── data/
│   │   ├── models.py        # Database models
│   │   └── create_db.py     # Database initialization
│   ├── routes/
│   │   ├── auth.py          # Authentication routes
│   │   ├── events.py        # Event routes
│   │   ├── event_organizer.py # Event organizer routes
│   │   └── admin.py         # Admin routes
│   ├── templates/           # HTML templates
│   └── static/              # CSS, JS, images
├── run.py                   # Main runner
└── README.md               # This file
```

## 🔧 Cấu hình

### Database
- **Host**: localhost
- **Port**: 3306
- **Database**: ticket_db
- **Username**: root
- **Password**: 12345

### Cloudinary
- **Cloud Name**: dgqx9xde1
- **API Key**: 455275651816759
- **API Secret**: 4ouN8Z8Hjj1ahlD7lH8sU21MWwA

## 🎯 Tính năng đã hoàn thành

### ✅ Authentication System
- Session-based authentication
- Email validation khi đăng ký
- Password hashing với MD5
- Flash messages cho thông báo
- Redirect sau đăng nhập/đăng xuất

### ✅ Event Management
- CRUD operations cho sự kiện
- Upload ảnh lên Cloudinary
- Phân loại sự kiện (online/offline)
- Trạng thái sự kiện (đang duyệt/đã duyệt/từ chối)

### ✅ Ticket Booking System
- Chọn loại vé và số lượng
- Chọn ghế ngồi tương tác
- Tính toán giá tiền
- Lưu trữ booking vào database

### ✅ Payment System
- QR code cho thanh toán
- Hỗ trợ nhiều phương thức (Bank, Momo)
- Xử lý thanh toán và tạo booking

### ✅ User Interface
- Responsive design
- Modern UI với CSS
- Interactive JavaScript
- QR code generation

## 🐛 Troubleshooting

### Lỗi "ModuleNotFoundError: No module named 'app'"
**Giải pháp**: Sử dụng `python -m app.run` thay vì `python app/run.py`

### Lỗi database connection
**Giải pháp**: 
1. Kiểm tra MySQL server đang chạy
2. Kiểm tra thông tin kết nối trong `app/__init__.py`
3. Chạy lại `python -m app.data.create_db`

### Lỗi Flask-Login
**Giải pháp**: Đã chuyển sang session-based authentication, không còn sử dụng Flask-Login

## 👥 Team
**Phát triển bởi QLDAPM Team**

## 📄 License
© 2024 TicketBox Clone. Tất cả quyền được bảo lưu.

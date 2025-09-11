# 🎫 **TicketBox Clone – Hệ thống đặt vé sự kiện trực tuyến**

## 📖 **Giới thiệu**
**TicketBox Clone** là một hệ thống đặt vé sự kiện trực tuyến được xây dựng bằng **Flask**.  
Ứng dụng cho phép:

- Người dùng đăng ký/đăng nhập, tìm kiếm, mua vé và chọn ghế ngồi.  
- Người tổ chức sự kiện có thể đăng tải và quản lý sự kiện.  
- Thanh toán nhanh chóng bằng **QR code** với nhiều phương thức.  

Dự án được thiết kế theo mô hình **MVC (Model–View–Controller)**, dễ bảo trì và mở rộng.  

---

## 🚀 **Hướng dẫn chạy ứng dụng**

### 1️⃣ **Cài đặt môi trường & dependencies**
```bash
pip install flask flask-sqlalchemy pymysql qrcode[pil] cloudinary
2️⃣ Cấu hình Database
Đảm bảo MySQL server đang chạy.
Tạo database ticket_db với charset utf8mb4.
Nếu cần, cập nhật thông tin kết nối tại app/__init__.py.
3️⃣ Khởi tạo Database
python -m app.data.create_db
4️⃣ Chạy ứng dụng
Có 2 cách chạy:
Cách 1: File run.py tại thư mục gốc
python run.py
Cách 2: Module app
python -m app.run
5️⃣ Truy cập ứng dụng
Mở trình duyệt: 👉 http://localhost:5000

🔐 Tính năng nổi bật
🧑‍💻 Authentication
Đăng ký tài khoản qua email (có kiểm tra hợp lệ).

Đăng nhập/đăng xuất, bảo mật bằng session.

Hash mật khẩu với MD5.

Redirect & flash message hỗ trợ UX tốt hơn.

🎉 Sự kiện
Xem, tìm kiếm và phân loại sự kiện (online/offline).

Chi tiết sự kiện đầy đủ thông tin.

CRUD sự kiện cho event organizer.

Upload ảnh sự kiện qua Cloudinary.

Quản lý trạng thái sự kiện: đang duyệt / đã duyệt / từ chối.

🎟️ Đặt vé
Chọn loại vé & số lượng.

Chọn ghế ngồi trực quan.

Tính toán tổng tiền tự động.

Lưu booking vào database.

💳 Thanh toán & QR Code
Thanh toán bằng QR code (Momo, Bank, …).

Tạo QR code riêng cho mỗi vé.

Hỗ trợ xác thực vé qua QR code.

🖥️ Giao diện người dùng
Responsive design, hỗ trợ mobile & desktop.

UI hiện đại với CSS & JS.

Tích hợp QR code trực tiếp trên giao diện vé.

🏗️ Cấu trúc dự án
OnlineTicketProject/
├── app/
│   ├── __init__.py             # Flask app factory
│   ├── run.py                  # App runner
│   ├── data/
│   │   ├── models.py           # Database models
│   │   └── create_db.py        # Database initialization
│   ├── routes/
│   │   ├── auth.py             # Authentication routes
│   │   ├── events.py           # Event routes
│   │   ├── event_organizer.py  # Event organizer routes
│   │   └── admin.py            # Admin routes
│   ├── templates/              # HTML templates
│   └── static/                 # CSS, JS, images
├── run.py                      # Main runner
└── README.md                   # Project documentation
⚙️ Cấu hình
Database
Host: localhost

Port: 3306

Database: ticket_db

Username: root

Password: 12345

Cloudinary
Cloud Name: dgqx9xde1

API Key: 455275651816759

API Secret: 4ouN8Z8Hjj1ahlD7lH8sU21MWwA

⚠️ Khuyến nghị: Không commit thông tin API/Secret trực tiếp lên repo public.
👉 Hãy sử dụng file .env để bảo mật.

🎯 Tính năng đã hoàn thiện
Authentication (session-based, email validation, password hashing)

Event management (CRUD, Cloudinary, status)

Ticket booking (seat selection, price calculation, DB persistence)

Payment system (QR code, nhiều phương thức thanh toán)

UI/UX (responsive, QR integration, JS interactive)

🐞 Troubleshooting
❌ Lỗi ModuleNotFoundError: No module named 'app'
👉 Giải pháp:

bash
Sao chép mã
python -m app.run
thay vì:

bash
Sao chép mã
python app/run.py
❌ Lỗi kết nối Database
👉 Kiểm tra:

MySQL server có đang chạy không.

Thông tin kết nối trong app/__init__.py.

Đã chạy python -m app.data.create_db chưa.

❌ Lỗi Flask-Login
👉 Hệ thống đã chuyển sang session-based auth, không còn dùng Flask-Login.

📚 Tài liệu hỗ trợ
Flask Documentation

SQLAlchemy ORM

Cloudinary API Docs

QRCode Python Library

MySQL Official Docs

👥 Team phát triển
QLDAPM Team – Nhóm nghiên cứu và phát triển hệ thống đặt vé trực tuyến.

Vai trò bao gồm:

Backend Development

Frontend Development

Database Design

UI/UX Design

📄 License
© 2024 TicketBox Clone. All rights reserved.
Phần mềm phát triển nhằm mục đích học tập & nghiên cứu, không sử dụng cho mục đích thương mại.

# test_email.py
from datetime import datetime
from app import create_app, mail
from app.utils import generate_ticket_qr, send_ticket_email  # đổi app.utils thành nơi chứa hàm của bạn

app = create_app()

with app.app_context():
    tickets_test = [
        # Vé offline, có ghế cụ thể
        {
            "ticket_id": 101,
            "event": "Hội thảo AI",
            "event_time": datetime(2025, 8, 20, 9, 0),
            "event_address": "Hội trường A",
            "seat": ["A1", "A2"],
            "quantity": 2,
            "user": "Nguyễn Văn A"
        },
        # Vé offline, ghế sẽ sắp xếp sau khi check-in
        {
            "ticket_id": 102,
            "event": "Hội thảo AI",
            "event_time": datetime(2025, 8, 20, 9, 0),
            "event_address": "Hội trường A",
            "seat": "Sẽ được sắp xếp ghế sau khi check-in",
            "quantity": 1,
            "user": "Nguyễn Văn A"
        },
        # Vé online
        {
            "ticket_id": 103,
            "event": "Workshop Python Online",
            "event_time": datetime(2025, 8, 25, 14, 0),
            "event_address": "https://zoom.us/j/123456789",
            "seat": None,
            "quantity": 3,
            "user": "Nguyễn Văn A"
        }
    ]

    # Test 1️⃣: Tạo QR code cho từng vé
    for t in tickets_test:
        qr_buf = generate_ticket_qr(t)
        filename = f"qr_test_{t['ticket_id']}.png"
        with open(filename, "wb") as f:
            f.write(qr_buf.getvalue())
        print(f"✅ QR code đã tạo: {filename}")

    # Test 2️⃣: Gửi email cho tất cả vé
    send_ticket_email("2254052006bong@ou.edu.vn", tickets_test)


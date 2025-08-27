import pytest
from io import BytesIO
from datetime import datetime
import app.utils as utils


def test_generate_ticket_qr():
    ticket_info = {"event": "Music Night", "ticket_id": "ABC123"}
    buf = utils.generate_ticket_qr(ticket_info)

    # Trả về buffer hợp lệ
    assert isinstance(buf, BytesIO)
    data = buf.getvalue()
    assert len(data) > 50  # phải có dữ liệu PNG


def test_send_ticket_email(app, monkeypatch):
    sent_messages = []

    # Mock mail.send để không gửi thật
    def fake_send(msg):
        sent_messages.append(msg)

    monkeypatch.setattr(utils.mail, "send", fake_send)

    ticket = {
        "event": "Concert 2024",
        "ticket_type": "VIP",
        "ticket_id": "TCK123",
        "seat": ["A1", "A2"],
        "quantity": 2,
        "event_time": datetime(2024, 12, 31, 20, 0),
        "event_address": "123 Đường ABC",
        "user": "Test User"
    }

    with app.app_context():
        utils.send_ticket_email("test@example.com", [ticket])

    # Kiểm tra có 1 email được gửi
    assert len(sent_messages) == 1
    msg = sent_messages[0]

    # Kiểm tra cơ bản của email
    assert msg.subject == "🎫 Vé sự kiện của bạn"
    assert "test@example.com" in msg.recipients
    assert "Concert 2024" in msg.html
    assert "TCK123" in msg.html

    # Kiểm tra có attach QR code
    qr_attachments = [a for a in msg.attachments if a.filename.startswith("qr")]
    assert len(qr_attachments) >= 1
    assert qr_attachments[0].content_type == "image/png"

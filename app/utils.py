import qrcode
import json
from io import BytesIO
from datetime import datetime

from flask import current_app
from flask_mail import Message
from app import mail

def generate_ticket_qr(ticket_info):

    data = json.dumps(ticket_info, default=str, ensure_ascii=False)
    qr = qrcode.QRCode(version=1, box_size=10, border=4)
    qr.add_data(data)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    buffered = BytesIO()
    img.save(buffered, format="PNG")
    buffered.seek(0)
    return buffered


def send_ticket_email(to_email, tickets):
    html_parts = [
        """
        <html>
        <body style="
            margin:0;
            padding:0;
            font-family: Arial, sans-serif;
            background-color:#f0f2f5;
            color:#333;
        ">
            <!-- Header -->
            <div style="
                text-align:center;
                padding:30px 10px;
                background: linear-gradient(145deg, #ffe6f0, #fff0f5);
            ">
                <h1 style="margin:0; color:#d81b60;">🎫 Vé sự kiện của bạn</h1>
                <p style="margin:5px 0 0 0; color:#555;">Bạn có thể quét QR code để check-in. Giữ vé này cẩn thận!</p>
            </div>
        """
    ]

    inline_images = []

    for idx, t in enumerate(tickets):
        # Ghế
        seats = t.get("seat")
        seats_str = ", ".join(seats) if isinstance(seats, list) else str(seats or "—")

        quantity = t.get("quantity", 1)

        # Thời gian
        event_time = t.get("event_time")
        if isinstance(event_time, datetime):
            event_time_str = event_time.strftime("%d/%m/%Y %H:%M")
        else:
            event_time_str = str(event_time or "Chưa có")

        # QR code
        cid = f"qr{idx}"
        qr_buf = generate_ticket_qr(t)
        inline_images.append((cid, qr_buf.getvalue()))

        # Địa điểm
        event_address = t.get("event_address", "Chưa có")
        if str(event_address).startswith("http"):
            address_html = f'<a href="{event_address}" target="_blank" style="color:#d81b60;">{event_address}</a>'
        else:
            address_html = f'<span style="color:#333;">{event_address}</span>'

        # HTML vé
        html_parts.append(f"""
            <div style="
                background: linear-gradient(145deg, #ffffff, #ffe6f0);
                padding:25px;
                margin:20px auto;
                border-radius:15px;
                box-shadow:0 8px 20px rgba(0,0,0,0.12);
                display:flex;
                flex-wrap:wrap;
                align-items:center;
                max-width:600px;
            ">
                <div style="flex:1; min-width:200px;">
                    <h3 style="
                        margin:0 0 10px 0;
                        color:#d81b60;
                        font-size:18px;
                    ">{t['event']}</h3>
                    <p style="margin:4px 0; font-size:14px; color:#555;"><strong>Loại vé:</strong> {t.get('ticket_type','—')}</p>
                    <p style="margin:4px 0; font-size:14px;"><strong>Thời gian:</strong> {event_time_str}</p>
                    <p style="margin:4px 0; font-size:14px;"><strong>Địa điểm:</strong> {address_html}</p>
                    <p style="margin:4px 0; font-size:14px;"><strong>Vé ID:</strong> {t['ticket_id']}</p>
                    <p style="margin:4px 0; font-size:14px;"><strong>Ghế:</strong> {seats_str}</p>
                    <p style="margin:4px 0; font-size:14px;"><strong>Số lượng:</strong> {quantity}</p>
                    <p style="margin:4px 0; font-size:14px; color:#555;"><strong>Người sở hữu:</strong> {t.get('user','—')}</p>
                </div>
                <div style="flex-shrink:0; text-align:center; margin-top:10px;">
                    <img src="cid:{cid}" alt="QR code vé" width="150" style="
                        border:3px solid #d81b60;
                        border-radius:12px;
                        box-shadow:0 4px 12px rgba(216,27,96,0.3);
                    "/>
                </div>
            </div>
        """)

    # Footer
    html_parts.append("""
        <div style="
            text-align:center;
            padding:20px 10px;
            color:#777;
            font-size:12px;
        ">
            <p>Vui lòng giữ mã QR này để check-in sự kiện.</p>
            <p>&copy;2024 TicketBox Clone. Tất cả quyền được bảo lưu.</p>
            <p>Phát triển bởi QLDAPM Team </p>
        </div>
        </body>
        </html>
    """)

    html_content = "\n".join(html_parts)

    # Gửi email
    with current_app.app_context():
        msg = Message(
            subject="Vé sự kiện của bạn",
            recipients=[to_email],
            html=html_content,
            sender=current_app.config.get("MAIL_USERNAME")
        )

        # Đính kèm QR code inline
        for cid, data in inline_images:
            msg.attach(
                filename=f"{cid}.png",
                content_type="image/png",
                data=data,
                disposition="inline",
                headers={"Content-ID": f"<{cid}>"}
            )

        try:
            mail.send(msg)
            print(f"Email vé đã gửi tới {to_email}")
        except Exception as e:
            print(f"Lỗi gửi email: {e}")

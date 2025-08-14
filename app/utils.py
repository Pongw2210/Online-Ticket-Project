import qrcode
import base64
from io import BytesIO
import json

from flask import current_app
from flask_mail import Message
from app import mail
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from PIL import Image

# =============================
# QR CODE GENERATOR
# =============================
def generate_ticket_qr(ticket_info):
    data = json.dumps(ticket_info, default=str)
    qr = qrcode.QRCode(version=1, box_size=10, border=4)
    qr.add_data(data)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    buffered = BytesIO()
    img.save(buffered, format="PNG")
    buffered.seek(0)
    return buffered

def qr_to_base64(ticket_info):
    buffered = generate_ticket_qr(ticket_info)
    img_base64 = base64.b64encode(buffered.getvalue()).decode()
    return f"data:image/png;base64,{img_base64}"

# =============================
# GENERATE PDF FOR MULTIPLE TICKETS
# =============================
def generate_tickets_pdf(tickets):
    buffer = BytesIO()
    c = canvas.Canvas(buffer, pagesize=A4)
    width, height = A4
    y_pos = height - 30*mm

    for t in tickets:
        c.setFont("Helvetica-Bold", 14)
        c.drawString(20*mm, y_pos, f"Sự kiện: {t['event']}")
        y_pos -= 8*mm
        c.setFont("Helvetica", 12)
        event_time_str = t['event_time'].strftime("%d/%m/%Y %H:%M") if t.get('event_time') else "Chưa có"
        c.drawString(20*mm, y_pos, f"Thời gian: {event_time_str}")
        y_pos -= 6*mm
        c.drawString(20*mm, y_pos, f"Địa điểm: {t.get('event_address','Chưa có')}")
        y_pos -= 6*mm
        seats_str = ", ".join(t['seat'])
        c.drawString(20*mm, y_pos, f"Vé ID: {t['ticket_id']}")
        y_pos -= 6*mm
        c.drawString(20*mm, y_pos, f"Ghế: {seats_str}")
        y_pos -= 6*mm
        c.drawString(20*mm, y_pos, f"Khách: {t['user']}")
        y_pos -= 10*mm

        # Chuyển BytesIO QR code sang PIL Image
        qr_img_buffer = generate_ticket_qr(t)
        qr_img_buffer.seek(0)
        qr_pil = Image.open(qr_img_buffer)

        c.drawInlineImage(qr_pil, 150*mm, y_pos, width=40*mm, height=40*mm)
        y_pos -= 50*mm

        if y_pos < 60*mm:
            c.showPage()
            y_pos = height - 30*mm

    c.save()
    buffer.seek(0)
    return buffer

# =============================
# SEND EMAIL HTML + PDF
# =============================
def send_ticket_email(to_email, tickets):
    """
    tickets: list dict chứa ticket info
    """
    # PDF
    pdf_buffer = generate_tickets_pdf(tickets)

    # HTML
    html = """
    <html>
    <body style="font-family: Arial,sans-serif; background-color:#f4f4f4; padding:20px;">
        <h2 style="color:#333;">🎫 Vé sự kiện của bạn</h2>
        <p>Dưới đây là thông tin vé đã mua. Bạn có thể quét QR code hoặc tải PDF đính kèm.</p>
    """
    for t in tickets:
        seats_str = ", ".join(t["seat"])
        event_time_str = t['event_time'].strftime("%d/%m/%Y %H:%M") if t.get('event_time') else "Chưa có"
        qr_base64 = qr_to_base64(t)
        html += f"""
        <div style="background-color:#fff; padding:15px; margin-bottom:20px; border-radius:8px; box-shadow:0 2px 5px rgba(0,0,0,0.1);">
            <h3 style="margin:0; color:#444;">Sự kiện: {t['event']}</h3>
            <p style="margin:5px 0;">Thời gian: {event_time_str}</p>
            <p style="margin:5px 0;">Địa điểm: {t.get('event_address','Chưa có')}</p>
            <p style="margin:5px 0;">Vé ID: {t['ticket_id']}</p>
            <p style="margin:5px 0;">Ghế: {seats_str}</p>
            <img src="{qr_base64}" alt="QR code vé" width="150" style="margin-top:10px;"/>
        </div>
        """
    html += """
        <p style="color:#666;">Vui lòng giữ mã QR này để check-in sự kiện.</p>
    </body>
    </html>
    """

    with current_app.app_context():
        msg = Message(
            subject="🎫 Vé sự kiện của bạn",
            recipients=[to_email],
            html=html,
            sender=current_app.config['MAIL_USERNAME']
        )
        msg.attach("tickets.pdf", "application/pdf", pdf_buffer.read())
        try:
            mail.send(msg)
            print(f"Email vé đã gửi tới {to_email}")
        except Exception as e:
            print(f"Lỗi gửi email: {e}")

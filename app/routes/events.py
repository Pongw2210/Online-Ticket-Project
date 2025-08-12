import uuid

from flask import Blueprint, render_template, request, session, jsonify, redirect, url_for
from flask_login import current_user

from app.data.models import Event, EventTypeEnum, Seat, BookingSeat, Booking, StatusBookingEnum, BookingDetail
from app import dao, db
import requests
import hmac
import hashlib

import json
import qrcode
import io
import base64

events_bp = Blueprint("events", __name__)

@events_bp.route("/")
def home():
    search = request.args.get("q", "")
    events = Event.query

    if search:
        # Map từ query string sang Enum
        mapping = {
            "Nhạc sống": EventTypeEnum.NHAC_SONG,
            "Sân khấu & Nghệ thuật": EventTypeEnum.NGHE_THUAT,
            "Thể thao": EventTypeEnum.THE_THAO,
            "Khác": EventTypeEnum.KHAC
        }
        event_type_enum = mapping.get(search)

        if event_type_enum:
            events = events.filter(Event.event_type == event_type_enum)
        else:
            # Nếu không khớp enum, tìm theo tên
            events = events.filter(Event.name.ilike(f"%{search}%"))

    events = events.order_by(Event.start_datetime.desc()).all()
    return render_template("home.html", events=events, search=search)

@events_bp.route('/event/<int:event_id>')
def event_detail(event_id):
    event = Event.query.get_or_404(event_id)
    print("[DEBUG] image_url =", event.image_url)
    min_price = None
    if event.ticket_types:
        min_price = min(ticket.price for ticket in event.ticket_types)
    
    return render_template('event_detail.html', event=event, min_price=min_price)

@events_bp.route("/buy-ticket/<int:event_id>")
def buy_ticket(event_id):
    event = dao.get_event_by_id(event_id)
    ticket_types = dao.load_ticket_type(event_id)
    return render_template("buy_ticket/buy_ticket.html",event=event, ticket_types=ticket_types)

@events_bp.route("/pay-ticket/<int:event_id>")
def pay_ticket(event_id):
    event = dao.get_event_by_id(event_id)
    return render_template("buy_ticket/pay_ticket.html",event=event)

@events_bp.route("/booking/create", methods=["POST"])
def create_booking():
    data = request.get_json()
    tickets = data.get("tickets", [])
    total_price = data.get("totalPrice")
    event_id = data.get("eventId")

    if not tickets or not total_price or not event_id:
        return jsonify({"success": False, "message": "Dữ liệu không hợp lệ"}), 400

    if not current_user.is_authenticated:
        return jsonify({"success": False, "message": "Chưa đăng nhập"}), 401

    try:
        # Tạo booking tổng, không cần ticket_type_id hoặc quantity ở đây nữa
        booking = Booking(
            user_id=current_user.id,
            event_id=event_id,
            total_price=total_price,
            status=StatusBookingEnum.CHO_THANH_TOAN
        )
        db.session.add(booking)
        db.session.flush()  # để có booking.id

        for t in tickets:
            # Tạo booking detail cho từng loại vé
            detail = BookingDetail(
                booking_id=booking.id,
                ticket_type_id=t['id'],
                quantity=t['quantity'],
                unit_price=t['price']  # Giá đơn vị
            )
            db.session.add(detail)
            db.session.flush()  # để có detail.id

            # Nếu vé yêu cầu chọn ghế, lưu ghế
            if t.get("requires_seat"):
                for seat_code in t.get("selected_seats", []):
                    seat = Seat.query.filter_by(event_id=event_id, seat_code=seat_code).first()
                    if not seat:
                        db.session.rollback()
                        return jsonify({"success": False, "message": f"Seat {seat_code} không tồn tại"}), 400
                    booking_seat = BookingSeat(booking_id=booking.id, seat_id=seat.id)
                    db.session.add(booking_seat)

        db.session.commit()
        return jsonify({"success": True, "bookingId": booking.id})

    except Exception as e:
        db.session.rollback()
        return jsonify({"success": False, "message": "Lỗi server: " + str(e)}), 500

@events_bp.route("/payment/momo", methods=["POST"])
def payment_momo():
    data = request.get_json()

    endpoint = "https://test-payment.momo.vn/v2/gateway/api/create"
    accessKey = "F8BBA842ECF85"
    secretKey = "K951B6PE1waDMi640xX08PD3vg6EkVlz"
    partnerCode = "MOMO"
    redirectUrl = "http://localhost:5000/payment/return"  # URL trả về sau khi thanh toán
    ipnUrl = "http://localhost:5000/payment/ipn"          # URL callback thông báo kết quả

    orderId = data.get("orderId", str(uuid.uuid4()))
    amount = str(data.get("amount", 50000))
    orderInfo = data.get("orderInfo", "Thanh toán test")
    requestId = str(uuid.uuid4())
    requestType = "payWithMethod"

    raw_signature = (
        f"accessKey={accessKey}&amount={amount}&extraData="
        f"&ipnUrl={ipnUrl}&orderId={orderId}&orderInfo={orderInfo}"
        f"&partnerCode={partnerCode}&redirectUrl={redirectUrl}"
        f"&requestId={requestId}&requestType={requestType}"
    )

    h = hmac.new(secretKey.encode('utf-8'), raw_signature.encode('utf-8'), hashlib.sha256)
    signature = h.hexdigest()

    payload = {
        "partnerCode": partnerCode,
        "partnerName": "Test",
        "storeId": "MomoTestStore",
        "requestId": requestId,
        "amount": amount,
        "orderId": orderId,
        "orderInfo": orderInfo,
        "redirectUrl": redirectUrl,
        "ipnUrl": ipnUrl,
        "lang": "vi",
        "extraData": "",
        "requestType": requestType,
        "signature": signature
    }

    res = requests.post(endpoint, json=payload)
    result = res.json()

    return jsonify({"payUrl": result.get("payUrl")})

@events_bp.route("/payment/return")
def payment_return():
    params = request.args.to_dict()
    print("MoMo RETURN params:", params)  # In toàn bộ params trả về

    result_code = request.args.get("resultCode")
    order_id = request.args.get("orderId")  # Lấy orderId MoMo gửi về

    if not order_id:
        # Không có orderId, không thể xác định booking
        return redirect(url_for("events.home", _anchor="payment-failed"))

    try:
        # Giả sử orderId có dạng "order_123", tách lấy phần số phía sau dấu "_"
        booking_id = int(order_id.split('_')[-1])
    except (ValueError, IndexError):
        # Nếu không tách được hoặc chuyển sang int lỗi
        return redirect(url_for("events.home", _anchor="payment-failed"))

    booking = Booking.query.get(booking_id)
    if not booking:
        # Không tìm thấy booking tương ứng
        return redirect(url_for("events.home", _anchor="payment-failed"))

    if result_code == "0":
        # Thanh toán thành công, cập nhật trạng thái
        booking.status = StatusBookingEnum.DA_THANH_TOAN
        db.session.commit()
        return redirect(url_for("events.home", _anchor="payment-success"))
    else:
        # Thanh toán thất bại hoặc hủy
        booking.status = StatusBookingEnum.DA_HUY
        db.session.commit()
        return redirect(url_for("events.home", _anchor="payment-failed"))


#
#
# @events_bp.route("/payment/ipn", methods=["POST"])
# def payment_ipn():
#     data = request.get_json()
#     print("IPN từ MoMo:", data)
#     return "OK", 200

import uuid
from flask import Blueprint, render_template, flash, session
from flask_login import current_user
from app.data.models import Event, EventTypeEnum, Seat, BookingSeat, Booking, StatusBookingEnum, BookingDetail, \
    TicketType
from app import dao, db
import requests
import hmac
import hashlib
from urllib.parse import urlencode
from flask import Blueprint, request, redirect, jsonify, url_for
import datetime
import random
import string


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
    order_id = request.args.get("orderId")

    if not order_id:
        return redirect(url_for("events.home", _anchor="payment-failed"))

    try:
        booking_id = int(order_id.split('_')[-1])
    except (ValueError, IndexError):
        return redirect(url_for("events.home", _anchor="payment-failed"))

    booking = Booking.query.get(booking_id)
    if not booking:
        # Không tìm thấy booking tương ứng
        return redirect(url_for("events.home", _anchor="payment-failed"))

    if result_code == "0":
        booking.status = StatusBookingEnum.DA_THANH_TOAN

        for detail in booking.booking_details:
            ticket_type = detail.ticket_type
            if ticket_type:
                ticket_type.quantity = max(ticket_type.quantity - detail.quantity, 0)

        db.session.commit()
        return redirect(url_for("events.home", _anchor="payment-success"))
    else:
        BookingDetail.query.filter_by(booking_id=booking.id).delete()
        booking.status = StatusBookingEnum.DA_HUY
        db.session.commit()
        return redirect(url_for("events.home", _anchor="payment-failed"))

@events_bp.route("/payment/ipn", methods=["POST"])
def payment_ipn():
    data = request.get_json()
    print("IPN từ MoMo:", data)
    return "OK", 200

# Hàm tạo chữ ký HMAC SHA512 cho VNPAY
def hmac_sha512(key, data):
    return hmac.new(key.encode(), data.encode(), hashlib.sha512).hexdigest()

@events_bp.route("/payment/vnpay", methods=["POST"])
def payment_vnpay():
    data = request.get_json()

    vnp_url = "https://sandbox.vnpayment.vn/paymentv2/vpcpay.html"
    return_url = "http://localhost:5000/payment/return_vnpay"
    tmn_code = "F0ATDO1K"
    secret_key = "ZISV60HMEWJIF2KO5I7UWS35Z8N0K3NO"

    order_id = data.get("orderId", ''.join(random.choices(string.ascii_uppercase + string.digits, k=8)))
    amount = int(data.get("amount", 10000)) * 100
    order_info = data.get("orderInfo", f"Thanh toan don hang {order_id}")

    vnp_params = {
        "vnp_Version": "2.1.0",
        "vnp_Command": "pay",
        "vnp_TmnCode": tmn_code,
        "vnp_Amount": str(amount),
        "vnp_CurrCode": "VND",
        "vnp_TxnRef": order_id,
        "vnp_OrderInfo": order_info,
        "vnp_OrderType": "other",
        "vnp_Locale": "vn",
        "vnp_ReturnUrl": return_url,
        "vnp_IpAddr": request.remote_addr,
        "vnp_CreateDate": datetime.datetime.now().strftime("%Y%m%d%H%M%S"),
    }

    # Sắp xếp tham số và tạo query string
    sorted_params = sorted(vnp_params.items())
    query_string = urlencode(sorted_params)

    # Tạo secure hash
    secure_hash = hmac_sha512(secret_key, query_string)

    # Gắn vào URL
    payment_url = f"{vnp_url}?{query_string}&vnp_SecureHash={secure_hash}"

    return jsonify({"payUrl": payment_url})

@events_bp.route("/payment/return_vnpay")
def payment_return_vnpay():
    params = request.args.to_dict()
    print("VNPAY RETURN params:", params)

    received_hash = params.pop("vnp_SecureHash", None)
    params.pop("vnp_SecureHashType", None)

    secret_key = "ZISV60HMEWJIF2KO5I7UWS35Z8N0K3NO"
    sorted_params = sorted(params.items())
    query_string = urlencode(sorted_params)
    calculated_hash = hmac_sha512(secret_key, query_string)

    order_id = request.args.get("vnp_TxnRef")

    if not order_id or calculated_hash != received_hash:
        return redirect(url_for("events.home", _anchor="payment-failed"))

    booking_id = int(order_id.split('_')[-1])
    booking = Booking.query.get(booking_id)
    if not booking:
        return redirect(url_for("events.home", _anchor="payment-failed"))

    result_code = params.get("vnp_ResponseCode")

    if result_code == "00":
        booking.status = StatusBookingEnum.DA_THANH_TOAN

        for detail in booking.booking_details:
            ticket_type = detail.ticket_type
            if ticket_type:
                ticket_type.quantity = max(ticket_type.quantity - detail.quantity, 0)

        db.session.commit()
        return redirect(url_for("events.home", _anchor="payment-success"))
    else:

        BookingDetail.query.filter_by(booking_id=booking.id).delete()
        # BookingSeat.query.filter_by(booking_id=booking.id).delete()

        booking.status = StatusBookingEnum.DA_HUY
        db.session.commit()
        return redirect(url_for("events.home", _anchor="payment-failed"))


@events_bp.route("/payment/ipn", methods=["GET"])
def payment_ipn_vnpay():
    params = request.args.to_dict()
    print("IPN từ VNPAY:", params)
    return "OK", 200
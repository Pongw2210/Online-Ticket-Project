import json, uuid, hmac ,hashlib, random, string, requests,datetime
from urllib.parse import urlencode
from flask import (
    Blueprint, request, redirect,
    jsonify, url_for, current_app
)
from app import db
from app.utils import send_ticket_email
from app.data.models import ( EventFormatEnum,
    Seat, StatusSeatEnum, BookingSeat,
    Booking, StatusBookingEnum, Voucher
)

payment_bp = Blueprint("payment", __name__)

def process_success_booking(booking: Booking, final_price=None):

    booking.status = StatusBookingEnum.DA_THANH_TOAN
    if final_price:
        booking.final_price = final_price

    # Giảm số lượng vé
    for detail in booking.booking_details:
        ticket_type = detail.ticket_type
        if ticket_type:
            ticket_type.quantity = max(ticket_type.quantity - detail.quantity, 0)

    # Đánh dấu ghế đã đặt
    for detail in booking.booking_details:
        for seat_link in detail.booking_seats:
            seat_obj = Seat.query.get(seat_link.seat_id)
            if seat_obj:
                seat_obj.status = StatusSeatEnum.DA_DAT

    # Giảm số lượng voucher
    if booking.booking_vouchers:
        for bv in booking.booking_vouchers:
            voucher_obj = Voucher.query.get(bv.voucher_id)
            if voucher_obj and voucher_obj.quantity > 0:
                voucher_obj.quantity -= 1

    db.session.commit()

    # Tạo dữ liệu vé để gửi email
    tickets_for_email = []
    for detail in booking.booking_details:
        ticket_type = detail.ticket_type
        event = ticket_type.event

        # Xử lý địa điểm & ghế
        seat_display = None
        event_address = "Chưa có địa điểm"

        if event.event_format == EventFormatEnum.OFFLINE:
            event_offline = getattr(event, "event_offline", None)
            event_address = getattr(event_offline, "location", "Chưa có địa điểm")

            if getattr(event_offline, "has_seat", 0) == 1:
                if ticket_type.requires_seat == 1:
                    seat_codes = [
                        s.seat_code for s in Seat.query
                        .join(BookingSeat, BookingSeat.seat_id == Seat.id)
                        .filter(BookingSeat.booking_detail_id == detail.id)
                        .all()
                    ]
                    seat_display = seat_codes
                else:
                    seat_display = "Sẽ được sắp xếp ghế sau khi check-in"
        else:
            event_online = getattr(event, "event_online", None)
            event_address = getattr(event_online, "livestream_url", "Online")

        # Thông tin vé
        ticket_info = {
            "ticket_id": detail.id,
            "event": event.name,
            "ticket_type": ticket_type.name,
            "event_time": event.start_datetime,
            "event_address": event_address,
            "seat": seat_display,
            "quantity": detail.quantity,
            "user": booking.user.fullname
        }

        # Lưu QR code data
        detail.qr_code_data = json.dumps(ticket_info, ensure_ascii=False, default=str)
        db.session.add(detail)
        db.session.commit()

        tickets_for_email.append(ticket_info)

    # Gửi mail
    with current_app.app_context():
        try:
            send_ticket_email(booking.user.email, tickets_for_email)
            print(f"Email vé đã gửi tới {booking.user.email}")
        except Exception as e:
            print(f"Lỗi gửi email: {e}")

    return True

@payment_bp.route("/payment/momo", methods=["POST"])
def momo_payment():
    data = request.get_json()

    # ===== Thông tin MoMo sandbox =====
    endpoint = "https://test-payment.momo.vn/v2/gateway/api/create"
    accessKey = "F8BBA842ECF85"
    secretKey = "K951B6PE1waDMi640xX08PD3vg6EkVlz"
    partnerCode = "MOMO"
    redirectUrl = "http://localhost:5000/payment/return"
    ipnUrl = "http://localhost:5000/payment/ipn"

    # ===== Thông tin đơn hàng từ client =====
    orderId = data.get("orderId") or f"order_{data.get('bookingId', str(uuid.uuid4()))}"
    amount = str(data.get("amount", 50000))
    orderInfo = data.get("orderInfo", "Thanh toán vé sự kiện")
    requestId = str(uuid.uuid4())
    requestType = "payWithMethod"

    # ===== Tạo chữ ký HMAC =====
    raw_signature = (
        f"accessKey={accessKey}&amount={amount}&extraData="
        f"&ipnUrl={ipnUrl}&orderId={orderId}&orderInfo={orderInfo}"
        f"&partnerCode={partnerCode}&redirectUrl={redirectUrl}"
        f"&requestId={requestId}&requestType={requestType}"
    )
    signature = hmac.new(secretKey.encode('utf-8'), raw_signature.encode('utf-8'), hashlib.sha256).hexdigest()

    # ===== Payload gửi MoMo =====
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

    # ===== Gửi request tới MoMo =====
    try:
        res = requests.post(endpoint, json=payload)
        result = res.json()
        print("MoMo API response:", result)

        pay_url = result.get("payUrl")
        if not pay_url:
            return jsonify({"error": "Không lấy được link thanh toán", "raw": result}), 400

        return jsonify({"payUrl": pay_url})

    except Exception as e:
        print("Lỗi gửi request MoMo:", e)
        return jsonify({"error": "Có lỗi khi kết nối MoMo"}), 500

@payment_bp.route("/payment/return")
def payment_return():
    params = request.args.to_dict()
    print("MoMo RETURN params:", params)

    result_code = request.args.get("resultCode")
    order_id = request.args.get("orderId")

    if not order_id:
        return redirect(url_for("events.home", _anchor="payment-failed"))

    try:
        booking_id = int(order_id.split('_')[1])
    except (ValueError, IndexError):
        return redirect(url_for("events.home", _anchor="payment-failed"))

    booking = Booking.query.get(booking_id)
    if not booking:
        return redirect(url_for("events.home", _anchor="payment-failed"))

    if result_code == "0" :
        final_price = request.args.get("amount")
        try:
            final_price = float(final_price)
        except (TypeError, ValueError):
            final_price = None
        process_success_booking(booking, final_price)
        return redirect(url_for("events.home", _anchor="payment-success"))
    else:
        booking.status = StatusBookingEnum.DA_HUY
        db.session.commit()
        return redirect(url_for("events.home", _anchor="payment-failed"))

@payment_bp.route("/payment/ipn", methods=["POST"])
def payment_ipn():
    data = request.get_json()
    print("IPN từ MoMo:", data)
    return "OK", 200

def hmac_sha512(key, data):
    return hmac.new(key.encode(), data.encode(), hashlib.sha512).hexdigest()

@payment_bp.route("/payment/vnpay", methods=["POST"])
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

@payment_bp.route("/payment/return_vnpay")
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

    booking_id = int(order_id.split('_')[1])
    booking = Booking.query.get(booking_id)
    if not booking:
        return redirect(url_for("events.home", _anchor="payment-failed"))

    result_code = params.get("vnp_ResponseCode")

    if result_code == "00":
        final_price = request.args.get("vnp_Amount")
        try:
            final_price = float(final_price) / 100
        except (TypeError, ValueError):
            final_price = None
        process_success_booking(booking, final_price)
        return redirect(url_for("events.home", _anchor="payment-success"))
    else:
        booking.status = StatusBookingEnum.DA_HUY
        db.session.commit()
        return redirect(url_for("events.home", _anchor="payment-failed"))

@payment_bp.route("/payment/ipn", methods=["GET"])
def payment_ipn_vnpay():
    params = request.args.to_dict()
    print("IPN từ VNPAY:", params)
    return "OK", 200

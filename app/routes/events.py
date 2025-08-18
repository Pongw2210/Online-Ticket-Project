import uuid
from flask import Blueprint, render_template, flash, session, current_app
from flask_login import current_user, login_required
from sqlalchemy.orm import joinedload

from app.data.models import Event, EventTypeEnum, Seat, BookingSeat, Booking, StatusBookingEnum, BookingDetail, \
    TicketType, StatusSeatEnum, StatusEventEnum, EventFormatEnum, Voucher, TicketVoucher, BookingVoucher
from app import dao, db
import requests
import hmac
import hashlib
from urllib.parse import urlencode
from flask import Blueprint, request, redirect, jsonify, url_for
import datetime
import random
import string

from app.utils import send_ticket_email

events_bp = Blueprint("events", __name__)

@events_bp.route("/")
def home():
    search = request.args.get("q", "")
    # bắt đầu từ query, chưa .all()
    events = Event.query.filter_by(status=StatusEventEnum.DA_DUYET)

    if search:
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
            events = events.filter(Event.name.ilike(f"%{search}%"))

    # Chỉ .all() khi đã filter xong
    events = events.order_by(Event.start_datetime.desc()).all()
    return render_template("home.html", events=events, search=search)

@events_bp.route('/event/<int:event_id>')
def event_detail(event_id):
    event = Event.query.get_or_404(event_id)
    # Kiểm tra kiểu dữ liệu
    print("Type:", type(event.image_url))

    # In an toàn, escape ký tự lạ
    print("[DEBUG] image_url =", str(event.image_url).encode("unicode_escape"))
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
    print(data)
    tickets = data.get("tickets", [])
    total_price = data.get("totalPrice")
    event_id = data.get("eventId")
    voucher_id = data.get("voucherId")

    if not tickets or not total_price or not event_id:
        return jsonify({"success": False, "message": "Dữ liệu không hợp lệ"}), 400

    if not current_user.is_authenticated:
        return jsonify({"success": False, "message": "Chưa đăng nhập"}), 401

    try:
        booking = Booking(
            user_id=current_user.id,
            event_id=event_id,
            total_price=total_price,
            status=StatusBookingEnum.CHO_THANH_TOAN
        )
        db.session.add(booking)
        db.session.flush()  # để có booking.id

        if voucher_id:
            booking_voucher = BookingVoucher(
                booking_id =booking.id,
                voucher_id =voucher_id
            )
            db.session.add(booking_voucher)

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

            for seat_info in t.get("seats", []):
                seat_id = seat_info.get("seat_id")
                seat_code = seat_info.get("seat_code")

                seat = Seat.query.filter_by(id=seat_id).with_for_update().first()
                if not seat:
                    db.session.rollback()
                    return jsonify({"success": False, "message": f"Seat {seat_code} không tồn tại"}), 400
                if seat.status != StatusSeatEnum.TRONG:
                    db.session.rollback()
                    return jsonify({"success": False, "message": f"Seat {seat_code} đã được đặt"}), 400

                booking_seat = BookingSeat(
                    booking_id=booking.id,
                    seat_id=seat.id
                )
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
    orderInfo = data.get("orderInfo", "Thanh toán tests")
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

        for seat_link in booking.booking_seats:
            seat_obj = Seat.query.get(seat_link.seat_id)
            if seat_obj:
                seat_obj.status = StatusSeatEnum.DA_DAT

        db.session.commit()

        # ==== Lấy dữ liệu vé để gửi email ====
        tickets_for_email = []
        booking_details = BookingDetail.query.filter_by(booking_id=booking.id).all()

        for detail in booking_details:
            ticket_type = detail.ticket_type
            event = ticket_type.event

            seat_display = None
            event_address = "Chưa có địa điểm"

            if event.event_format == EventFormatEnum.OFFLINE:
                # Lấy thông tin địa điểm offline
                event_offline = getattr(event, "event_offline", None)
                event_address = getattr(event_offline, "location", "Chưa có địa điểm")

                if getattr(event_offline, "has_seat", 0) == 1:
                    if ticket_type.requires_seat == 1:
                        # Lấy danh sách ghế của booking
                        seat_codes = [
                            s.seat_code for s in Seat.query
                            .join(BookingSeat, BookingSeat.seat_id == Seat.id)
                            .filter(BookingSeat.booking_id == booking.id)
                            .all()
                        ]
                        seat_display = seat_codes
                    else:
                        seat_display = "Sẽ được sắp xếp ghế sau khi check-in"
                else:
                    seat_display = None

            else:  # ONLINE
                event_online = getattr(event, "event_online", None)
                event_address = getattr(event_online, "meeting_url", "Online")
                seat_display = None

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

            tickets_for_email.append(ticket_info)

            # Gửi email
        with current_app.app_context():
            try:
                send_ticket_email(booking.user.email, tickets_for_email)
                print(f"Email vé đã gửi tới {booking.user.email}")
            except Exception as e:
                print(f"Lỗi gửi email: {e}")

        return redirect(url_for("events.home", _anchor="payment-success"))
    else:
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

        for seat_link in booking.booking_seats:
            seat_obj = Seat.query.get(seat_link.seat_id)
            if seat_obj:
                seat_obj.status = StatusSeatEnum.DA_DAT

        if booking.booking_vouchers:
            for bv in booking.booking_vouchers:
                voucher_obj = Voucher.query.get(bv.voucher_id)
                if voucher_obj and voucher_obj.quantity > 0:
                    voucher_obj.quantity -= 1

        db.session.commit()

        # ==== Lấy dữ liệu vé để gửi email ====
        tickets_for_email = []
        booking_details = BookingDetail.query.filter_by(booking_id=booking.id).all()

        for detail in booking_details:
            ticket_type = detail.ticket_type
            event = ticket_type.event

            seat_display = None
            event_address = "Chưa có địa điểm"

            if event.event_format == EventFormatEnum.OFFLINE:
                # Lấy thông tin địa điểm offline
                event_offline = getattr(event, "event_offline", None)
                event_address = getattr(event_offline, "location", "Chưa có địa điểm")

                if getattr(event_offline, "has_seat", 0) == 1:
                    if ticket_type.requires_seat == 1:
                        # Lấy danh sách ghế của booking
                        seat_codes = [
                            s.seat_code for s in Seat.query
                            .join(BookingSeat, BookingSeat.seat_id == Seat.id)
                            .filter(BookingSeat.booking_id == booking.id)
                            .all()
                        ]
                        seat_display = seat_codes
                    else:
                        seat_display = "Sẽ được sắp xếp ghế sau khi check-in"
                else:
                    seat_display = None

            else:  # ONLINE
                event_online = getattr(event, "event_online", None)
                event_address = getattr(event_online, "meeting_url", "Online")
                seat_display = None

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

            tickets_for_email.append(ticket_info)

            # Gửi email
        with current_app.app_context():
            try:
                send_ticket_email(booking.user.email, tickets_for_email)
                print(f"Email vé đã gửi tới {booking.user.email}")
            except Exception as e:
                print(f"Lỗi gửi email: {e}")

        return redirect(url_for("events.home", _anchor="payment-success"))
    else:
        booking.status = StatusBookingEnum.DA_HUY
        db.session.commit()
        return redirect(url_for("events.home", _anchor="payment-failed"))

@events_bp.route("/payment/ipn", methods=["GET"])
def payment_ipn_vnpay():
    params = request.args.to_dict()
    print("IPN từ VNPAY:", params)
    return "OK", 200

@events_bp.route("/api/seats/<int:event_id>")
def get_seats(event_id):
    seats = Seat.query.filter_by(event_id=event_id).all()
    seat_list = []
    for seat in seats:
        seat_list.append({
            "id": seat.id,
            "name": seat.seat_code,
            "occupied": seat.status != StatusSeatEnum.TRONG
        })
    return jsonify(seat_list)


@events_bp.route('/my-ticket')
@login_required
def my_tickets():
    # Lấy tất cả booking đã thanh toán của user
    bookings = Booking.query.filter_by(user_id=current_user.id, status=StatusBookingEnum.DA_THANH_TOAN).all()

    tickets_for_user = []
    for booking in bookings:
        for detail in booking.booking_details:
            ticket_type = detail.ticket_type
            event = ticket_type.event

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
                            .filter(BookingSeat.booking_id == booking.id)
                            .all()
                        ]
                        seat_display = seat_codes
                    else:
                        seat_display = "Sẽ được sắp xếp ghế sau khi check-in"
            else:
                event_online = getattr(event, "event_online", None)
                event_address = getattr(event_online, "meeting_url", "Online")
                seat_display = None

            ticket_info = {
                "ticket_id": detail.id,
                "event": event.name,
                "ticket_type": ticket_type.name,
                "event_time": event.start_datetime,
                "event_address": event_address,
                "seat": seat_display,
                "quantity": detail.quantity,
                "user": current_user.fullname
            }
            tickets_for_user.append(ticket_info)

    return render_template("my_tickets.html", tickets=tickets_for_user)

@events_bp.route("/api/vouchers/<int:event_id>", methods=["POST"])
def get_event_vouchers(event_id):
    try:
        data = request.get_json()
        tickets = data.get("tickets", [])

        # Lấy ra danh sách ticket_type_id từ tickets
        ticket_type_ids = [t.get("id") for t in tickets if "id" in t]

        query = db.session.query(Voucher).filter(Voucher.event_id == event_id)

        if ticket_type_ids:
            query = query.filter(
                (Voucher.apply_all == True)
                | Voucher.id.in_(
                    db.session.query(TicketVoucher.voucher_id).filter(
                        TicketVoucher.ticket_type_id.in_(ticket_type_ids)
                    )
                )
            )
        else:
            query = query.filter(Voucher.apply_all == True)

        vouchers = query.distinct(Voucher.id).all()

        result = []
        for v in vouchers:
            item = {
                "id": v.id,
                "code": v.code,
                "discount_value": v.discount_value,
                "discount_type": v.discount_type.name if v.discount_type else None,
                "apply_all": v.apply_all,
                "ticket_types": [],
            }

            if not v.apply_all:
                item["ticket_types"] = [t.ticket_type_id for t in v.ticket_vouchers]

            result.append(item)

        return jsonify(result), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500







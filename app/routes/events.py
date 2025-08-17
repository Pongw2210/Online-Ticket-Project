import uuid
import datetime
import random
import string
import requests
import hmac
import hashlib
from urllib.parse import urlencode

from flask import Blueprint, render_template, request, redirect, jsonify, url_for, current_app
from flask_login import current_user, login_required

from app.data.models import (
    Event, EventTypeEnum, Seat, BookingSeat, Booking,
    StatusBookingEnum, BookingDetail, TicketType,
    StatusSeatEnum, StatusEventEnum, EventFormatEnum, Customer
)
from app import dao, db
from app.utils import send_ticket_email


events_bp = Blueprint("events", __name__)


@events_bp.route("/")
def home():
    search = request.args.get("q", "")
    events = Event.query.filter(Event.status == StatusEventEnum.DA_DUYET)

    if search:
        search_lower = search.lower()
        if search_lower in ["online", "trực tuyến"]:
            events = events.filter(Event.event_format == EventFormatEnum.ONLINE)
        elif search_lower in ["offline", "trực tiếp"]:
            events = events.filter(Event.event_format == EventFormatEnum.OFFLINE)
        else:
            mapping = {
                "nghệ thuật": EventTypeEnum.NGHE_THUAT,
                "thể thao": EventTypeEnum.THE_THAO,
                "nhạc sống": EventTypeEnum.NHAC_SONG,
                "khác": EventTypeEnum.KHAC,
            }
            if search_lower in mapping:
                events = events.filter(Event.event_type == mapping[search_lower])
            else:
                try:
                    event_type_enum = EventTypeEnum(search)
                    events = events.filter(Event.event_type == event_type_enum)
                except ValueError:
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
    return render_template("buy_ticket/buy_ticket.html", event=event, ticket_types=ticket_types)


@events_bp.route("/pay-ticket/<int:event_id>")
def pay_ticket(event_id):
    event = dao.get_event_by_id(event_id)
    return render_template("buy_ticket/pay_ticket.html", event=event)


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
        # Lấy customer, nếu chưa có thì tự tạo mới
        customer = Customer.query.filter_by(user_id=current_user.id).first()
        if not customer:
            customer = Customer(
                user_id=current_user.id,
                fullname=current_user.fullname,
                email=current_user.email
            )
            db.session.add(customer)
            db.session.flush()

        booking = Booking(
            user_id=current_user.id,
            event_id=event_id,
            total_price=total_price,
            status=StatusBookingEnum.CHO_THANH_TOAN
        )
        db.session.add(booking)
        db.session.flush()

        for t in tickets:
            booking = Booking(
                user_id=current_user.id,
                event_id=event_id,
                total_price=total_price,
                status=StatusBookingEnum.CHO_THANH_TOAN
            )
            db.session.add(booking)
            db.session.flush()
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
        return jsonify({"success": True, "bookingId": booking.id, "amount": booking.total_price})

    except Exception as e:
        db.session.rollback()
        return jsonify({"success": False, "message": "Lỗi server: " + str(e)}), 500


@events_bp.route("/payment/momo", methods=["POST"])
def payment_momo():
    data = request.get_json()

    booking_id = data.get("bookingId")
    amount = str(data.get("amount", 50000))
    orderInfo = data.get("orderInfo", "Thanh toán vé sự kiện")

    if not booking_id:
        return jsonify({"success": False, "message": "Thiếu bookingId"}), 400

    orderId = f"BOOKING_{booking_id}"
    requestId = str(uuid.uuid4())

    endpoint = "https://test-payment.momo.vn/v2/gateway/api/create"
    accessKey = "F8BBA842ECF85"
    secretKey = "K951B6PE1waDMi640xX08PD3vg6EkVlz"
    partnerCode = "MOMO"
    redirectUrl = "http://localhost:5000/payment/return"
    ipnUrl = "http://localhost:5000/payment/ipn"
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
    print("MoMo RESPONSE:", result)

    if "payUrl" not in result:
        return jsonify({"success": False, "message": result}), 400

    return jsonify({"payUrl": result.get("payUrl")})


@events_bp.route("/payment/return")
def payment_return():
    params = request.args.to_dict()
    print("MoMo RETURN params:", params)

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
        return redirect(url_for("events.home", _anchor="payment-failed"))

    if result_code == "0" and booking.status == StatusBookingEnum.CHO_THANH_TOAN:
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


def hmac_sha512(key, data):
    return hmac.new(key.encode(), data.encode(), hashlib.sha512).hexdigest()

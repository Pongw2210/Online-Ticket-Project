import string
import json
from datetime import datetime

from flask import Blueprint, render_template, redirect, url_for, request, jsonify, session
from flask_login import login_required, current_user

import cloudinary.uploader

from app import dao, db
from app.data.models import (
    UserEnum, User, Customer,
    Event, EventOffline, EventOnline, EventFormatEnum, EventTypeEnum, StatusEventEnum, EventRejectionLog,
    TicketType, DiscountTypeEnum, Voucher, TicketVoucher,
    Booking, BookingDetail, StatusBookingEnum,
    Seat, StatusSeatEnum,
    RefundRequest, RefundStatusEnum
)

event_organizer_bp = Blueprint("event_organizer", __name__, url_prefix="/organizer")

@event_organizer_bp.route("/home")
def home():
    # current_user = check_login()
    if not current_user:
        return redirect(url_for("auth.login"))

    # Chỉ cho phép người tổ chức vào
    if current_user.role != UserEnum.NGUOI_TO_CHUC:
        return redirect(url_for("events.home"))

    organizer_id = current_user.event_organizer.id
    search_query = request.args.get("q", "").strip()

    approved_events = dao.load_approved_events(organizer_id,search_query)
    pending_events  = dao.load_pending_events(organizer_id,search_query)
    hidden_events  = dao.load_hidden_events(organizer_id,search_query)
    rejected_events  = dao.load_rejected_events(organizer_id,search_query)

    return render_template("event_organizer/home_event_organizer.html",
                           current_user=current_user,
                           approved_events = approved_events,
                           pending_events = pending_events,
                           hidden_events = hidden_events,
                           rejected_events = rejected_events)

@event_organizer_bp.route("/new-event")
def create_event():
    # current_user = check_login()
    if not current_user:
        return redirect(url_for("auth.login"))

    if current_user.role != UserEnum.NGUOI_TO_CHUC:
        return redirect(url_for("events.home"))
    event_type = dao.load_event_type_enum()

    return render_template("event_organizer/create_event.html",current_user=current_user,event_type=event_type)

@event_organizer_bp.route('/api/create-event', methods=['POST'])
def create_event_api():
    if not current_user:
        return jsonify({"success": False, "message": "Vui lòng đăng nhập"}), 401

    try:
        # Upload ảnh lên Cloudinary
        image_file = request.files.get("image")
        if not image_file:
            return jsonify({"success": False, "message": "Thiếu ảnh sự kiện"}), 400

        upload_result = cloudinary.uploader.upload(image_file)
        image_url = upload_result.get("secure_url")

        # Lấy dữ liệu từ form
        name = request.form.get("name_event")
        description = request.form.get("description")
        rules = request.form.get("rules")
        performers = request.form.get("performers")
        organizer = request.form.get("organizer")
        event_format = request.form.get("event_format")
        event_type = request.form.get("event_type")
        start_time = request.form.get("start_time")
        end_time = request.form.get("end_time")
        tickets = request.form.get("tickets")
        has_seat_str = request.form.get("has_seat", "false")
        has_seat = has_seat_str.lower() == "true"

        num_rows = seats_per_row = None
        if has_seat:
            num_rows = request.form.get("num_rows")
            seats_per_row = request.form.get("seats_per_row")

        # Tạo sự kiện
        new_event = Event(
            name=name,
            description=description,
            rules=rules,
            authors=performers,
            producers=organizer,
            image_url=image_url,
            event_format=EventFormatEnum[event_format.upper()],
            event_type=EventTypeEnum[event_type],
            start_datetime=datetime.fromisoformat(start_time),
            end_datetime=datetime.fromisoformat(end_time),
            organizer_id=current_user.event_organizer.id
        )
        db.session.add(new_event)
        db.session.flush()  # lấy event_id

        # Thêm địa điểm
        if event_format == "offline":
            venue_name = request.form.get("venue_name")
            address = request.form.get("address")
            event_offline = EventOffline(
                venue_name=venue_name,
                location=address,
                has_seat=has_seat,
                event_id=new_event.id
            )
            db.session.add(event_offline)
        else:
            livestream_url = request.form.get("livestream_url")
            event_online = EventOnline(
                livestream_url=livestream_url,
                event_id=new_event.id
            )
            db.session.add(event_online)

        # Thêm vé
        ticket_list = json.loads(tickets)
        ticket_objects = []
        for t in ticket_list:
            ticket = TicketType(
                name=t['name'],
                price=float(t['price']),
                quantity=int(t['quantity']),
                requires_seat=bool(t.get('requires_seat', False)),
                benefits=t['benefits'],
                event_id=new_event.id
            )
            db.session.add(ticket)
            ticket_objects.append(ticket)

        # Tạo ghế nếu có chỗ ngồi
        if has_seat and num_rows and seats_per_row:
            num_rows = int(num_rows)
            seats_per_row = int(seats_per_row)
            row_labels = list(string.ascii_uppercase)[:num_rows]
            for row_label in row_labels:
                for seat_num in range(1, seats_per_row + 1):
                    seat_code = f"{row_label}{seat_num}"
                    seat = Seat(
                        event_id=new_event.id,
                        seat_code=seat_code,
                        status=StatusSeatEnum.TRONG
                    )
                    db.session.add(seat)
        db.session.commit()
        return jsonify({"success": True})

    except Exception as e:
        db.session.rollback()
        print("Error:", e)
        return jsonify({"success": False, "message": "Lỗi khi tạo sự kiện."}), 500

@event_organizer_bp.route('/api/<int:event_id>/hide',methods=['POST'])
def hide_event_api(event_id):
    event = Event.query.get(event_id)

    if not event:
        return jsonify({"message": "Không tìm thấy sự kiện."}), 404

    event.status= StatusEventEnum.DA_AN
    db.session.commit()

    return jsonify({"message": "Ẩn sự kiện thành công."}), 200

@event_organizer_bp.route('/api/<int:event_id>/show',methods=['POST'])
def show_event_api(event_id):
    event = Event.query.get(event_id)

    if not event:
        return jsonify({"message": "Không tìm thấy sự kiện."}), 404

    event.status= StatusEventEnum.DA_DUYET
    db.session.commit()

    return jsonify({"message": "Công khai sự kiện thành công."}), 200

@event_organizer_bp.route('/api/<int:event_id>/rejected_reason')
def get_rejected_reason_api(event_id):
    rejection_log = EventRejectionLog.query.filter_by(event_id=event_id).first()
    print(rejection_log)
    if rejection_log:
        return jsonify({"reason": rejection_log.reason})
    return jsonify({"reason": None})

@event_organizer_bp.route("/edit-event/<int:event_id>")
@login_required
def edit_event(event_id):
    if current_user.role != UserEnum.NGUOI_TO_CHUC:
        return redirect(url_for("events.home"))

    event = dao.get_event_by_id(event_id)
    event_type = dao.load_event_type_enum()
    is_offline = event.event_format == EventFormatEnum.OFFLINE

    ticket_types = TicketType.query.filter_by(event_id=event_id)

    return render_template("event_organizer/edit_event.html",
                           current_user=current_user,
                           event_type=event_type,
                           event=event,
                           is_offline=is_offline,
                           ticket_types=ticket_types)

@event_organizer_bp.route('/api/<int:event_id>/edit', methods=['POST'])
def edit_event_api(event_id):
    try:
        # Tìm sự kiện cũ
        event = Event.query.get(event_id)
        if not event:
            return jsonify({"success": False, "message": "Không tìm thấy sự kiện"}), 404

        # Lấy ảnh mới (nếu có)
        image_file = request.files.get("image")
        existing_image_url = request.form.get("existing_image_url")
        if image_file:
            upload_result = cloudinary.uploader.upload(image_file)
            event.image_url = upload_result.get("secure_url")
        elif existing_image_url:
            event.image_url = existing_image_url

        name = request.form.get("name_event")
        description = request.form.get("description")
        rules = request.form.get("rules")
        performers = request.form.get("performers")
        organizer = request.form.get("organizer")
        event_format = request.form.get("event_format")
        event_type = request.form.get("event_type")
        start_time = request.form.get("start_time")
        end_time = request.form.get("end_time")

        # Cập nhật vào DB
        event.name = name
        event.description = description
        event.rules = rules
        event.authors = performers
        event.producers = organizer
        event.event_format = EventFormatEnum[event_format.upper()]
        event.event_type = EventTypeEnum[event_type]
        event.start_datetime = datetime.fromisoformat(start_time)
        event.end_datetime = datetime.fromisoformat(end_time)
        event.status = StatusEventEnum.DANG_DUYET

        # Cập nhật offline/online
        if event.event_format == EventFormatEnum.OFFLINE:
            venue_name = request.form.get("venue_name")
            address = request.form.get("address")

            if not venue_name or not address:
                return jsonify({"success": False, "message": "Vui lòng điền đầy đủ địa điểm sự kiện"}), 400

            if event.event_offline:
                event.event_offline.venue_name = venue_name
                event.event_offline.location = address
            else:
                new_offline = EventOffline(venue_name=venue_name, location=address, event_id=event.id)
                db.session.add(new_offline)
        else:
            livestream_url = request.form.get("livestream_url")
            if event.event_online:
                event.event_online.livestream_url = livestream_url
            else:
                new_online = EventOnline(livestream_url=livestream_url, event_id=event.id)
                db.session.add(new_online)

        # Cập nhật các loại vé (xoá hết tạo lại đơn giản nhất)
        import json
        tickets = json.loads(request.form.get("tickets", "[]"))

        TicketType.query.filter_by(event_id=event.id).delete()
        for t in tickets:
            ticket = TicketType(
                name=t['name'],
                price=float(t['price']),
                quantity=int(t['quantity']),
                event_id=event.id
            )
            db.session.add(ticket)

        db.session.commit()
        return jsonify({"success": True})

    except Exception as e:
        db.session.rollback()
        import traceback
        traceback.print_exc()
        return jsonify({"success": False, "message": "Lỗi khi cập nhật sự kiện."}), 500

@event_organizer_bp.route('/api/<int:event_id>/delete',methods=['DELETE'])
def delete_event_api(event_id):
    event = Event.query.get(event_id)

    if not event:
        return jsonify({"message": "Không tìm thấy sự kiện."}), 404

    db.session.delete(event)
    db.session.commit()

    return jsonify({"message": "Xóa sự kiện thành công."}), 200

@event_organizer_bp.route("/api/<int:event_id>/ticket-types")
def get_ticket_types(event_id):
    ticket_types = TicketType.query.filter_by(event_id=event_id).all()
    return jsonify([
        {"id": t.id, "name": t.name, "price": t.price}
        for t in ticket_types
    ])

@event_organizer_bp.route('/api/create-voucher', methods=['POST'])
def create_voucher():
    try:
        data = request.get_json()

        event_id = int(data.get("event_id"))
        code = data.get("code", "").strip()
        discount_value_raw = data.get("discount_value", "").strip()
        quantity = int(data.get("quantity", 1))
        start_date = datetime.fromisoformat(data.get("start_date"))
        end_date = datetime.fromisoformat(data.get("end_date"))
        apply_all = data.get("apply_all", False)
        ticket_ids = data.get("ticket_ids", [])

        # Xác định discount_type
        if "%" in discount_value_raw:
            discount_type = DiscountTypeEnum.PHAN_TRAM
            discount_value = float(discount_value_raw.replace("%",""))
        else:
            discount_type = DiscountTypeEnum.SO_TIEN
            discount_value = float(discount_value_raw)

        # Check trùng mã voucher trong cùng sự kiện
        if db.session.query(Voucher).filter_by(code=code, event_id=event_id).first():
            return jsonify({"error": "Mã voucher đã tồn tại trong sự kiện này"}), 400

        # Tạo voucher mới
        voucher = Voucher(
            event_id=event_id,
            code=code,
            discount_type=discount_type,
            discount_value=discount_value,
            quantity=quantity,
            start_date=start_date,
            end_date=end_date,
            apply_all=apply_all
        )
        db.session.add(voucher)
        db.session.commit()  # Commit để có voucher.id

        # Lưu TicketVoucher nếu không áp dụng tất cả vé
        if not apply_all and ticket_ids:
            ticket_vouchers = [
                TicketVoucher(voucher_id=voucher.id, ticket_type_id=int(tid))
                for tid in ticket_ids
            ]
            db.session.add_all(ticket_vouchers)
            db.session.commit()

        return jsonify({"message": "Tạo voucher thành công", "voucher_id": voucher.id}), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

@event_organizer_bp.route("/api/save-ticket", methods=["POST"])
def save_ticket():
    data = request.get_json()

    event_id = data.get("event_id")
    name = data.get("name")
    quantity = data.get("quantity")
    price = data.get("price")
    benefits = data.get("benefit")
    requires_seat = data.get("requires_seat", 0)

    if not event_id or not name or not quantity or not price:
        return jsonify({"success": False, "message": "Thiếu dữ liệu"})

    existing_ticket = TicketType.query.filter_by(event_id=event_id, name=name).first()
    if existing_ticket:
        return jsonify({"success": False, "message": "Tên vé đã tồn tại trong sự kiện này"})

    try:
        ticket = TicketType(
            event_id=event_id,
            name=name,
            quantity=quantity,
            price=price,
            benefits=benefits,
            requires_seat=requires_seat
        )
        db.session.add(ticket)
        db.session.commit()

        return jsonify({"success": True})
    except Exception as e:
        db.session.rollback()
        return jsonify({"success": False, "message": str(e)})

@event_organizer_bp.route("/ticket-history")
@login_required
def ticket_history():
    history = (
        db.session.query(
            User.username,
            Customer.fullname,
            Customer.email,
            Booking.booking_date,
            TicketType.name.label("ticket_type"),
            BookingDetail.quantity,
            (BookingDetail.unit_price * BookingDetail.quantity).label("price"),
            Event.name.label("event_name")
        )
        .join(BookingDetail, BookingDetail.booking_id == Booking.id)
        .join(TicketType, TicketType.id == BookingDetail.ticket_type_id)
        .join(Event, Event.id == Booking.event_id)
        .join(User, User.id == Booking.user_id)
        .join(Customer, Customer.user_id == User.id)
        .filter(Event.organizer_id == current_user.event_organizer.id)
        .filter(Booking.status == StatusBookingEnum.DA_THANH_TOAN)
        .all()
    )
    return render_template("event_organizer/ticket_history.html", history=history)

@event_organizer_bp.route("/<int:event_id>")
def event_detail(event_id):
    event = Event.query.get_or_404(event_id)
    vouchers = Voucher.query.filter_by(event_id=event.id).all()
    return render_template('event_organizer/event_detail_organizer.html',
                           event=event,vouchers=vouchers)

@event_organizer_bp.route("/refund-requests")
@login_required
def refund_requests():
    if current_user.role != UserEnum.NGUOI_TO_CHUC:
        return redirect(url_for("events.home"))

    organizer_id = current_user.event_organizer.id
    refunds = (
        db.session.query(RefundRequest)
        .join(RefundRequest.booking_detail)     # join BookingDetail
        .join(Booking, Booking.id == BookingDetail.booking_id)
        .join(Event, Event.id == Booking.event_id)
        .filter(Event.organizer_id == organizer_id)
        .all()
    )
    return render_template("event_organizer/refund_requests.html", refunds=refunds)

@event_organizer_bp.route("/api/refund/<int:refund_id>/<string:action>", methods=['POST'])
@login_required
def handle_refund(refund_id, action):
    if current_user.role != UserEnum.NGUOI_TO_CHUC:
        return jsonify({"success": False, "message": "Không có quyền"}), 403

    refund = RefundRequest.query.get(refund_id)
    if not refund:
        return jsonify({"success": False, "message": "Không tìm thấy yêu cầu"}), 404

    try:
        detail = refund.booking_detail
        booking = detail.booking

        if action == "approve":
            # 1) Đánh dấu yêu cầu hoàn
            refund.status = RefundStatusEnum.DONG_Y

            # 2) Tính số lượng hoàn
            refunded_qty = detail.quantity or 0

            # 3) Hoàn lại tồn vé cho TicketType
            try:
                if detail.ticket_type and refunded_qty > 0:
                    detail.ticket_type.quantity = (detail.ticket_type.quantity or 0) + refunded_qty
            except Exception:
                pass  # phòng trường hợp model khác tên thuộc tính

            # 4) Mở ghế (nếu có ghế) & xoá liên kết đặt ghế (nếu dùng bảng trung gian)
            # Lưu ý: tuỳ mô hình của bạn. Nếu BookingDetail có quan hệ booking_seats -> seat
            # thì dùng vòng lặp dưới. Nếu bạn dùng bảng BookingSeat rời, hãy query theo booking_id.
            try:
                if hasattr(detail, "booking_seats"):
                    for bs in list(detail.booking_seats):
                        if bs.seat:
                            bs.seat.status = StatusSeatEnum.TRONG
                        db.session.delete(bs)  # huỷ liên kết giữ ghế
            except Exception:
                pass

            # 5) Trả lại voucher (nếu có gán voucher cho booking)
            # Nếu có bảng liên kết BookingVoucher / booking.booking_vouchers
            try:
                if hasattr(booking, "booking_vouchers"):
                    for bv in list(booking.booking_vouchers):
                        if bv.voucher:
                            # trả lại số lượng cho voucher
                            bv.voucher.quantity = (bv.voucher.quantity or 0) + 1
                        db.session.delete(bv)  # huỷ liên kết voucher với booking
            except Exception:
                pass

            # 6) Giảm tổng tiền booking trước rồi set quantity của detail = 0
            if refunded_qty > 0:
                # Tổng gốc trước khi giảm giá
                original_total = sum(d.unit_price * d.quantity for d in booking.booking_details)

                refund_amount = 0
                if original_total > 0:
                    discount_ratio = booking.total_price / original_total
                    refund_amount = (detail.unit_price or 0) * refunded_qty * discount_ratio

                booking.total_price = (booking.total_price or 0) - refund_amount
                if booking.total_price < 0:
                    booking.total_price = 0

            detail.quantity = 0

            # 7) Nếu tất cả chi tiết đều đã hoàn (quantity == 0) → set booking = ĐÃ HOÀN
            all_refunded = True
            for d in booking.booking_details:
                # còn quantity > 0 là chưa hoàn hết
                if (d.quantity or 0) > 0:
                    all_refunded = False
                    break
            if all_refunded:
                booking.status = StatusBookingEnum.DA_HOAN

        elif action == "reject":
            refund.status = RefundStatusEnum.TU_CHOI

        db.session.commit()
        return jsonify({"success": True, "message": "Cập nhật thành công"})

    except Exception as e:
        db.session.rollback()
        import traceback; traceback.print_exc()
        return jsonify({"success": False, "message": "Lỗi server: " + str(e)}), 500

@event_organizer_bp.route("/scan-qr")
@login_required
def scan_qr():
    return render_template("event_organizer/scan_qr.html")

@event_organizer_bp.route("/api/booking/check-in", methods=["POST"])
@login_required
def scan_qr_checkin():
    try:
        data = request.get_json()
        qr_raw = data.get("qr_code")

        if not qr_raw:
            return jsonify({"success": False, "message": "Thiếu dữ liệu QR"}), 400

        print("QR raw:", qr_raw, "| type:", type(qr_raw))

        # Nếu qr_raw đã là dict (trường hợp gửi trực tiếp JSON)
        if isinstance(qr_raw, dict):
            qr_data = qr_raw
        else:
            # Trường hợp qr_raw là string JSON
            try:
                qr_data = json.loads(qr_raw)
            except Exception:
                return jsonify({"success": False, "message": "QR không hợp lệ"}), 400

        ticket_id = qr_data.get("ticket_id")
        if not ticket_id:
            return jsonify({"success": False, "message": "QR thiếu ticket_id"}), 400

        detail = BookingDetail.query.get(ticket_id)
        if not detail:
            return jsonify({"success": False, "message": "Vé không tồn tại"}), 404

        if detail.booking.status != StatusBookingEnum.DA_THANH_TOAN:
            return jsonify({"success": False, "message": "Vé chưa được thanh toán"}), 400

        if detail.check_in == 1:
            return jsonify({"success": False, "message": "Vé đã được check-in trước đó"}), 400

        detail.check_in = 1
        detail.check_in_at = datetime.utcnow()
        db.session.commit()

        return jsonify({
            "success": True,
            "message": "Check-in thành công",
        })

    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500

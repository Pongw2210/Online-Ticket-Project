import string
import json

from flask import Blueprint, render_template, redirect, url_for,request, jsonify, session
from flask_login import login_required, current_user

from app import dao,db
from app.data.models import UserEnum, Event, EventOffline, EventOnline, TicketType, EventFormatEnum, EventTypeEnum, \
    StatusEventEnum, EventRejectionLog, Seat, StatusSeatEnum, DiscountTypeEnum, Voucher, TicketVoucher
import cloudinary.uploader
from datetime import datetime

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

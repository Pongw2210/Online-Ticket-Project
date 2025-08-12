from flask import Blueprint, render_template, redirect, url_for,request, jsonify, session
from flask_login import login_required, current_user

from app import dao,db
from app.data.models import UserEnum, Event, EventOffline, EventOnline, TicketType, EventFormatEnum, EventTypeEnum, \
    StatusEventEnum, EventRejectionLog
import cloudinary.uploader
from datetime import datetime

event_organizer_bp = Blueprint("event_organizer", __name__, url_prefix="/organizer")
#
# def check_login():
#     """Kiểm tra đăng nhập và trả về user"""
#     if "user_id" not in session:
#         return None
#     return User.query.get(session["user_id"])

@event_organizer_bp.route("/home")
def home():
    # current_user = check_login()
    if not current_user:
        return redirect(url_for("auth.login"))
    
    # Chỉ cho phép người tổ chức vào
    if current_user.role != UserEnum.NGUOI_TO_CHUC:
        return redirect(url_for("events.home"))

    organizer_id = current_user.event_organizer.id

    approved_events = dao.load_approved_events(organizer_id)
    pending_events  = dao.load_pending_events(organizer_id)
    hidden_events  = dao.load_hidden_events(organizer_id)
    rejected_events  = dao.load_rejected_events(organizer_id)

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
        has_seat_str = request.form.get("has_seat", "false")  # từ form gửi lên string "true"/"false"
        has_seat = True if has_seat_str.lower() == "true" else False

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
            organizer_id=current_user.event_organizer.id  # cần đăng nhập
        )

        db.session.add(new_event)
        db.session.flush()  # để lấy event_id

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
        import json
        ticket_list = json.loads(tickets)
        for t in ticket_list:
            ticket = TicketType(
                name=t['name'],
                price=float(t['price']),
                quantity=int(t['quantity']),
                requires_seat=bool(t.get('requires_seat', False)),
                benefits = t['benefits'],
                event_id=new_event.id
            )
            db.session.add(ticket)

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


from flask import Blueprint, render_template, redirect, url_for,request, jsonify, session
from app import dao,db
from app.data.models import UserEnum,Event, EventOffline, EventOnline, TicketType, EventFormatEnum, EventTypeEnum, User
import cloudinary.uploader
from datetime import datetime

event_organizer_bp = Blueprint("event_organizer", __name__, url_prefix="/organizer")

def check_login():
    """Kiểm tra đăng nhập và trả về user"""
    if "user_id" not in session:
        return None
    return User.query.get(session["user_id"])

@event_organizer_bp.route("/home")
def home():
    current_user = check_login()
    if not current_user:
        return redirect(url_for("auth.login"))
    
    # Chỉ cho phép người tổ chức vào
    if current_user.role != UserEnum.NGUOI_TO_CHUC:
        return redirect(url_for("events.home"))
    return render_template("event_organizer/home_event_organizer.html", current_user=current_user)


@event_organizer_bp.route("/new-event")
def create_event():
    current_user = check_login()
    if not current_user:
        return redirect(url_for("auth.login"))
    
    if current_user.role != UserEnum.NGUOI_TO_CHUC:
        return redirect(url_for("events.home"))
    event_type = dao.load_event_type_enum()

    return render_template("event_organizer/create_event.html",current_user=current_user,event_type=event_type)

@event_organizer_bp.route('/api/create-event', methods=['POST'])
def create_event_api():
    current_user = check_login()
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
                event_id=new_event.id
            )
            db.session.add(ticket)

        db.session.commit()
        return jsonify({"success": True})

    except Exception as e:
        db.session.rollback()
        print("Error:", e)
        return jsonify({"success": False, "message": "Lỗi khi tạo sự kiện."}), 500

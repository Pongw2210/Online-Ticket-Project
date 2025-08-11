from flask import Blueprint, render_template, request, session, jsonify
from flask_login import current_user

from app.data.models import Event, User, TicketType, Booking, EventTypeEnum
from app import db, dao
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
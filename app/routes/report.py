# app/blueprints/report.py
from datetime import datetime, timedelta
from flask import Blueprint, render_template, request, jsonify, Response
from flask_login import login_required, current_user
from sqlalchemy import func

from app.data.models import (
    db, Event, TicketType, Booking, BookingDetail, User, Customer,
    StatusBookingEnum
)

report_bp = Blueprint("report", __name__, url_prefix="/organizer/report")


# -------- Helpers --------
def _parse_date(s, fallback=None):
    if not s:
        return fallback
    try:
        return datetime.strptime(s, "%Y-%m-%d").date()
    except Exception:
        return fallback


def _paid():
    return Booking.status == StatusBookingEnum.DA_THANH_TOAN


def _organizer_filter():
    return Event.organizer_id == current_user.event_organizer.id


# -------- Page --------
@report_bp.route("/", methods=["GET"])
@login_required
def dashboard():
    events = Event.query.filter(_organizer_filter()).order_by(Event.start_datetime.desc()).all()
    return render_template("event_organizer/report.html", events=events)


# -------- API: Tổng quan nhanh --------
@report_bp.route("/api/summary", methods=["GET"])
@login_required
def api_summary():
    start = _parse_date(request.args.get("start"))
    end = _parse_date(request.args.get("end"))
    event_id = request.args.get("event_id", type=int)

    # Tổng doanh thu = sum Booking.total_price (đã trừ voucher)
    q_revenue = db.session.query(
        func.coalesce(func.sum(Booking.total_price), 0)
    ).join(Event, Booking.event_id == Event.id) \
     .filter(_organizer_filter(), _paid())

    # Tổng số vé
    q_tickets = db.session.query(
        func.coalesce(func.sum(BookingDetail.quantity), 0)
    ).join(Booking, BookingDetail.booking_id == Booking.id) \
     .join(Event, Booking.event_id == Event.id) \
     .filter(_organizer_filter(), _paid())

    if event_id:
        q_revenue = q_revenue.filter(Event.id == event_id)
        q_tickets = q_tickets.filter(Event.id == event_id)
    if start:
        q_revenue = q_revenue.filter(Booking.booking_date >= start)
        q_tickets = q_tickets.filter(Booking.booking_date >= start)
    if end:
        q_revenue = q_revenue.filter(Booking.booking_date <= end + timedelta(days=1))
        q_tickets = q_tickets.filter(Booking.booking_date <= end + timedelta(days=1))

    return jsonify({
        "total_revenue": float(q_revenue.scalar() or 0),
        "total_tickets": int(q_tickets.scalar() or 0)
    })


# -------- API: Doanh thu theo thời gian --------
@report_bp.route("/api/revenue_by_date", methods=["GET"])
@login_required
def api_revenue_by_date():
    start = _parse_date(request.args.get("start"))
    end = _parse_date(request.args.get("end"))
    event_id = request.args.get("event_id", type=int)
    group_by = request.args.get("group_by", "day")

    date_expr = {
        "day": func.date(Booking.booking_date),
        "month": func.to_char(Booking.booking_date, "YYYY-MM"),
        "year": func.to_char(Booking.booking_date, "YYYY")
    }.get(group_by, func.date(Booking.booking_date))

    q = db.session.query(
        date_expr.label("label"),
        func.sum(Booking.total_price).label("revenue")
    ).join(Event, Booking.event_id == Event.id) \
     .filter(_organizer_filter(), _paid())

    if event_id:
        q = q.filter(Event.id == event_id)
    if start:
        q = q.filter(Booking.booking_date >= start)
    if end:
        q = q.filter(Booking.booking_date <= end + timedelta(days=1))

    data = q.group_by("label").order_by("label").all()
    return jsonify({
        "labels": [str(r.label) for r in data],
        "values": [float(r.revenue or 0) for r in data]
    })


# -------- API: Doanh thu theo loại vé --------
@report_bp.route("/api/revenue_by_ticket", methods=["GET"])
@login_required
def api_revenue_by_ticket():
    start = _parse_date(request.args.get("start"))
    end = _parse_date(request.args.get("end"))
    event_id = request.args.get("event_id", type=int)

    # Vẫn tính theo BookingDetail (doanh thu gốc theo loại vé)
    q = db.session.query(
        TicketType.name.label("label"),
        func.sum(BookingDetail.unit_price * BookingDetail.quantity).label("revenue")
    ).join(TicketType, BookingDetail.ticket_type_id == TicketType.id) \
     .join(Booking, BookingDetail.booking_id == Booking.id) \
     .join(Event, Booking.event_id == Event.id) \
     .filter(_organizer_filter(), _paid())

    if event_id:
        q = q.filter(Event.id == event_id)
    if start:
        q = q.filter(Booking.booking_date >= start)
    if end:
        q = q.filter(Booking.booking_date <= end + timedelta(days=1))

    data = q.group_by(TicketType.name).order_by(TicketType.name).all()
    return jsonify({
        "labels": [r.label for r in data],
        "values": [float(r.revenue or 0) for r in data]
    })


# -------- API: Vé bán ra theo sự kiện --------
@report_bp.route("/api/tickets_by_event", methods=["GET"])
@login_required
def api_tickets_by_event():
    start = _parse_date(request.args.get("start"))
    end = _parse_date(request.args.get("end"))
    event_id = request.args.get("event_id", type=int)

    q = db.session.query(
        Event.id, Event.name,
        func.coalesce(func.sum(BookingDetail.quantity), 0).label("tickets")
    ).join(Booking, BookingDetail.booking_id == Booking.id) \
     .join(Event, Booking.event_id == Event.id) \
     .filter(_organizer_filter(), _paid())

    if event_id:
        q = q.filter(Event.id == event_id)
    if start:
        q = q.filter(Booking.booking_date >= start)
    if end:
        q = q.filter(Booking.booking_date <= end + timedelta(days=1))

    data = q.group_by(Event.id, Event.name).order_by(Event.start_datetime.desc()).all()
    return jsonify({
        "labels": [r.name for r in data],
        "values": [int(r.tickets or 0) for r in data]
    })


# -------- API: Vé đã bán vs còn lại --------
@report_bp.route("/api/ticket_stock", methods=["GET"])
@login_required
def api_ticket_stock():
    start = _parse_date(request.args.get("start"))
    end = _parse_date(request.args.get("end"))

    total_q = db.session.query(
        Event.id, Event.name,
        func.coalesce(func.sum(TicketType.quantity), 0).label("total")
    ).join(TicketType, TicketType.event_id == Event.id) \
     .filter(_organizer_filter()) \
     .group_by(Event.id, Event.name) \
     .subquery()

    sold_q = db.session.query(
        Event.id.label("eid"),
        func.coalesce(func.sum(BookingDetail.quantity), 0).label("sold")
    ).join(Booking, BookingDetail.booking_id == Booking.id) \
     .join(Event, Booking.event_id == Event.id) \
     .filter(_organizer_filter(), _paid())

    if start:
        sold_q = sold_q.filter(Booking.booking_date >= start)
    if end:
        sold_q = sold_q.filter(Booking.booking_date <= end + timedelta(days=1))
    sold_q = sold_q.group_by(Event.id).subquery()

    q = db.session.query(
        total_q.c.name,
        total_q.c.total,
        func.coalesce(sold_q.c.sold, 0).label("sold")
    ).outerjoin(sold_q, sold_q.c.eid == total_q.c.id)

    rows = q.all()
    return jsonify({
        "labels": [r.name for r in rows],
        "sold": [int(r.sold or 0) for r in rows],
        "remaining": [max(int(r.total or 0) - int(r.sold or 0), 0) for r in rows]
    })


# -------- API: Top khách hàng --------
@report_bp.route("/api/top_customers", methods=["GET"])
@login_required
def api_top_customers():
    start = _parse_date(request.args.get("start"))
    end = _parse_date(request.args.get("end"))
    limit = request.args.get("limit", default=10, type=int)
    event_id = request.args.get("event_id", type=int)

    q = db.session.query(
        Customer.fullname.label("name"),
        func.sum(BookingDetail.quantity).label("tickets"),
        func.sum(Booking.total_price).label("spent")
    ).join(Booking, BookingDetail.booking_id == Booking.id) \
     .join(User, Booking.user_id == User.id) \
     .join(Customer, Customer.user_id == User.id) \
     .join(Event, Booking.event_id == Event.id) \
     .filter(_organizer_filter(), _paid())

    if event_id:
        q = q.filter(Event.id == event_id)
    if start:
        q = q.filter(Booking.booking_date >= start)
    if end:
        q = q.filter(Booking.booking_date <= end + timedelta(days=1))

    rows = q.group_by(Customer.fullname).order_by(func.sum(BookingDetail.quantity).desc()).limit(limit).all()

    return jsonify({
        "rows": [
            {"name": r.name, "tickets": int(r.tickets or 0), "spent": float(r.spent or 0)}
            for r in rows
        ]
    })


# -------- Export CSV --------
@report_bp.route("/export/top_customers.csv", methods=["GET"])
@login_required
def export_top_customers():
    resp = api_top_customers().json
    lines = ["Khach hang,Sove,Doanhthu"]
    for r in resp["rows"]:
        lines.append(f"{r['name']},{r['tickets']},{int(r['spent'])}")
    csv = "\n".join(lines)
    return Response(
        csv,
        mimetype="text/csv",
        headers={"Content-Disposition": "attachment; filename=top_customers.csv"}
    )

from flask import Blueprint, render_template, redirect, url_for, request
from app.data.models import Event, EventRejectionLog, Booking
from app import db
from datetime import datetime
from app.data.models import StatusEventEnum
from sqlalchemy import func
from flask_admin import BaseView, expose
from app import admin_view



admin_bp = Blueprint('admin_view', __name__, url_prefix='/admin')

@admin_bp.route("/approve-events")
def approve_events():
    events = Event.query.filter_by(status=StatusEventEnum.DANG_DUYET).all()
    return render_template("admin/approval.html", events=events)
@admin_bp.route("/admin")
def admin_dashboard():
    return render_template("admin/dashboard.html")

@admin_bp.route("/approve/<int:event_id>", methods=["POST"])
def approve(event_id):
    event = Event.query.get_or_404(event_id)
    event.status = StatusEventEnum.DA_DUYET
    db.session.commit()
    return redirect(url_for("admin_view.approve_events"))

@admin_bp.route("/reject/<int:event_id>", methods=["POST"])
def reject(event_id):
    reason = request.form.get("reason")
    event = Event.query.get_or_404(event_id)

    # Cập nhật trạng thái
    event.status = StatusEventEnum.TU_CHOI

    # Ghi log từ chối vào bảng riêng
    log = EventRejectionLog(
        event_id=event.id,
        reason=reason,
        rejected_at=datetime.now()
    )
    db.session.add(log)
    db.session.commit()
    return redirect(url_for("admin_view.approve_events"))


from flask import Blueprint, render_template, redirect, url_for, request, session, current_app
from app.data.models import Event, EventRejectionLog, Booking, Admin
from app import db
from datetime import datetime
from app.data.models import StatusEventEnum
from sqlalchemy import func
from flask_admin import BaseView, expose
import os
from werkzeug.utils import secure_filename
import time
from flask_login import login_required, current_user
admin_bp = Blueprint('admin_view', __name__, url_prefix='/admin')

# ===================== DASHBOARD + APPROVAL =====================

@admin_bp.route("/approve-events")
def approve_events():
    events = Event.query.filter_by(status=StatusEventEnum.DANG_DUYET).all()
    return render_template("admin/approval.html", events=events)

@admin_bp.route("/")
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
    event.status = StatusEventEnum.TU_CHOI
    log = EventRejectionLog(
        event_id=event.id,
        reason=reason,
        rejected_at=datetime.now()
    )
    db.session.add(log)
    db.session.commit()
    return redirect(url_for("admin_view.approve_events"))

# ===================== ADMIN PROFILE ROUTE =====================

@admin_bp.route("/profile")
def admin_profile():
    user_id = session.get('user_id')
    if not user_id:
        return redirect(url_for('auth.login'))  # chuyển về login nếu chưa đăng nhập

    admin_data = Admin.query.filter_by(user_id=user_id).first()
    if not admin_data:
        return "Không tìm thấy thông tin admin", 404

    return render_template("admin/profile.html", admin=admin_data)

# ===================== FLASK-ADMIN CUSTOM VIEW =====================

class AdminProfileView(BaseView):
    @expose('/')
    def index(self):
        user_id = session.get('user_id')
        if not user_id:
            return redirect(url_for('auth.login'))

        admin_data = Admin.query.filter_by(user_id=user_id).first()
        return self.render('admin/profile_admin.html', admin=admin_data)



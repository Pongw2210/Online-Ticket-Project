from flask import Blueprint, render_template, redirect, url_for
from flask_login import login_required, current_user

from app import dao
from app.data.models import UserEnum

event_organizer_bp = Blueprint("event_organizer", __name__, url_prefix="/organizer")

@event_organizer_bp.route("/home")
@login_required
def home():
    # Chỉ cho phép người tổ chức vào
    if current_user.role != UserEnum.NGUOI_TO_CHUC:
        return redirect(url_for("events.home"))
    return render_template("event_organizer/home_event_organizer.html", current_user=current_user)


@event_organizer_bp.route("/new-event")
@login_required
def create_event():
    if current_user.role != UserEnum.NGUOI_TO_CHUC:
        return redirect(url_for("events.home"))
    event_type = dao.load_event_type_enum()

    return render_template("event_organizer/create_event.html",current_user=current_user,event_type=event_type)
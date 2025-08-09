from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from app.data.models import User
from app import db
import re

auth_bp = Blueprint("auth", __name__)

def is_valid_email(email):
    """Kiểm tra email có hợp lệ không"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form["username"]
        email = request.form["email"]
        password = request.form["password"]

        # Kiểm tra email hợp lệ
        if not is_valid_email(email):
            flash("Email không hợp lệ!")
            return redirect(url_for("auth.register"))

        # Kiểm tra người dùng đã tồn tại
        if User.query.filter((User.username == username) | (User.email == email)).first():
            flash("Tên đăng nhập hoặc email đã tồn tại!")
            return redirect(url_for("auth.register"))

        # Tạo người dùng mới
        new_user = User(username=username, email=email)
        new_user.set_password(password)

        db.session.add(new_user)
        db.session.commit()

        flash("Đăng ký thành công. Vui lòng đăng nhập.")
        return redirect(url_for("auth.login"))

    return render_template("auth.html", is_login=False)


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        user = dao.auth_user(username, password)

        # user = User.query.filter_by(username=username).first()
        # if user and user.check_password(password):

        if user:
            login_user(user)  # Đăng nhập flask-login
            if user.role == UserEnum.ADMIN:
                return redirect(url_for("admin_view.approve_events"))
            elif user.role == UserEnum.NGUOI_TO_CHUC:
                return redirect(url_for("event_organizer.home"))
            else:
                return redirect(url_for("events.home"))
        else:
            flash("Tên đăng nhập hoặc mật khẩu không đúng!")

    return render_template("auth.html", is_login=True)



# ✅ Gắn route cho logout
@auth_bp.route("/logout")
def logout():
    session.pop("user_id", None)
    flash("Đăng xuất thành công!")
    return redirect(url_for("events.home"))

from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from app import db,dao,login
from app.data.models import User, UserEnum
from flask_login import current_user, login_user, logout_user
auth_bp = Blueprint("auth", __name__)


@login.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form["username"]
        email = request.form["email"]
        password = request.form["password"]

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
    if current_user.is_authenticated:
        return redirect('/')

    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        user = dao.auth_user(username,password)

        if user:
            login_user(user)
            if user.role == UserEnum.ADMIN:
                return redirect(url_for(("admin_view.approve_events")))
            elif user.role == UserEnum.NGUOI_TO_CHUC:
                return redirect(url_for('event_organizer.home'))

            return redirect(url_for("events.home"))
        else:
            flash("Tên đăng nhập hoặc mật khẩu không đúng!")

    return render_template("auth.html", is_login=True)

@auth_bp.route("/logout")
def logout_my_user():
    logout_user()
    return redirect(url_for("events.home"))

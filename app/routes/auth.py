from flask import Blueprint, render_template, request, redirect, url_for, flash
from app import db, dao, login
from app.data.models import User, UserEnum, Customer
from flask_login import login_user, logout_user
from datetime import datetime

from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from app import db, dao, login
from app.data.models import User, UserEnum
from flask_login import current_user, login_user, logout_user


auth_bp = Blueprint("auth", __name__)

@login.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        fullname = request.form.get("fullname")
        email = request.form.get("email")
        gender = request.form.get("gender")
        dob_str = request.form.get("dob")
        number_phone = request.form.get("number_phone")
        password = request.form.get("password")

        # Chuyển đổi ngày sinh
        try:
            dob = datetime.strptime(dob_str, "%Y-%m-%d")
        except Exception:
            flash("Ngày sinh không hợp lệ!")
            return redirect(url_for("auth.register"))

        # Kiểm tra email đã tồn tại
        if User.query.filter_by(email=email).first():
            flash("Email đã tồn tại!")
            return redirect(url_for("auth.register"))

        # Tạo user mới
        new_user = User(
            username=email,  # Hoặc bạn muốn tách username riêng
            email=email,
            role=UserEnum.KHACH_HANG
        )
        new_user.set_password(password)
        db.session.add(new_user)
        db.session.flush()  # Để lấy new_user.id mà chưa commit

        # Tạo customer mới gắn với user
        new_customer = Customer(
            fullname=fullname,
            email=email,
            gender=gender,
            dob=dob,
            number_phone=number_phone,
            user_id=new_user.id
        )
        db.session.add(new_customer)

        # Commit cả hai bản ghi
        db.session.commit()

        flash("Đăng ký thành công. Vui lòng đăng nhập.")
        return redirect(url_for("auth.login"))

    return render_template("auth/register.html")

@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        user = dao.auth_user(username, password)

        if user:
            login_user(user)

            #  Admin → chuyển về trang Flask-Admin

            if user.role == UserEnum.ADMIN:
                return redirect("/admin/")

            elif user.role == UserEnum.NGUOI_TO_CHUC:
                return redirect(url_for('event_organizer.home'))
            else:
                return redirect(url_for("events.home"))
        else:
            flash("Tên đăng nhập hoặc mật khẩu không đúng!")

    return render_template("auth/login.html")

@auth_bp.route("/logout")
def logout_my_user():
    logout_user()
    return redirect(url_for("events.home"))

@auth_bp.route('/user_info')
def user_info():
    return render_template('user_info.html')

import cloudinary.uploader
from flask import Blueprint, render_template, request, redirect, url_for, flash, session, jsonify, current_app
from app import db, dao, login
from app.data.models import User, UserEnum, Customer
from flask_login import current_user, login_user, logout_user, login_required
from datetime import datetime
import os, time
from uuid import uuid4
from werkzeug.utils import secure_filename
from functools import wraps


UPLOAD_FOLDER = os.path.join("app", "static", "uploads", "avatars")
ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "gif"}
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


auth_bp = Blueprint("auth", __name__)

@login.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

def login_required_json(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            return jsonify({"status": "error", "message": "Bạn chưa đăng nhập"}), 401
        return f(*args, **kwargs)
    return decorated_function

@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        fullname = request.form.get("fullname")
        email = request.form.get("email")
        gender = request.form.get("gender")
        dob_str = request.form.get("dob")
        number_phone = request.form.get("number_phone")
        username = request.form.get("username")
        password = request.form.get("password")

        try:
            dob = datetime.strptime(dob_str, "%Y-%m-%d")
        except Exception:
            flash("Ngày sinh không hợp lệ!")
            return redirect(url_for("auth.register"))

        if User.query.filter_by(email=email).first():
            flash("Email đã tồn tại!")
            return redirect(url_for("auth.register"))

        new_user = User(username=username, email=email, role=UserEnum.KHACH_HANG)
        new_user.set_password(password)
        db.session.add(new_user)
        db.session.flush()

        new_customer = Customer(
            fullname=fullname, email=email, gender=gender, dob=dob,
            number_phone=number_phone, user_id=new_user.id
        )
        db.session.add(new_customer)
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
            if user.role == UserEnum.ADMIN:
                return redirect("/admin/")
            elif user.role == UserEnum.NGUOI_TO_CHUC:
                return redirect(url_for("event_organizer.home"))
            else:
                return redirect(url_for("events.home"))
        else:
            flash("Tên đăng nhập hoặc mật khẩu không đúng!")

    return render_template("auth/login.html")

@auth_bp.route("/logout")
def logout_my_user():
    logout_user()
    return redirect(url_for("auth.login"))

@auth_bp.route("/user_info")
@login_required
def user_info():
    return render_template("auth/user_info.html")

@auth_bp.route("/upload_avatar", methods=["POST"])
@login_required
def upload_avatar():
    if "avatar" not in request.files:
        return jsonify({"status": "error", "message": "Không có file upload"}), 400

    file = request.files["avatar"]

    try:
        # Upload lên Cloudinary
        result = cloudinary.uploader.upload(
            file,
            folder="avatars",  # tạo thư mục avatars trên cloudinary
            public_id=f"user_{current_user.id}_{int(time.time())}",
            overwrite=True,
            resource_type="image"
        )

        avatar_url = result.get("secure_url")

        # Lưu vào DB
        current_user.avatar = avatar_url
        db.session.commit()

        return jsonify({
            "status": "success",
            "message": "Upload avatar thành công!",
            "avatar_url": avatar_url + f"?t={int(time.time())}"  # tránh cache
        })

    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500
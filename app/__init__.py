from flask import Flask
from flask_login import LoginManager
from flask_mail import Mail
from flask_sqlalchemy import SQLAlchemy
import cloudinary
from app.admin_view import flask_admin

db = SQLAlchemy()
login = LoginManager()
mail = Mail()

def create_app():
    app = Flask(__name__)

    # App secret + Config DB
    app.secret_key = "%$@%^@%#^VGHGD"
    app.config["SQLALCHEMY_DATABASE_URI"] = "mysql+pymysql://root:123456@localhost/ticket_db?charset=utf8mb4"
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False


    # Cloudinary config
    cloudinary.config(
        cloud_name='dgqx9xde1',
        api_key='455275651816759',
        api_secret='4ouN8Z8Hjj1ahlD7lH8sU21MWwA'
    )

    app.config['MAIL_SERVER'] = 'smtp.gmail.com'  # Ví dụ dùng Gmail
    app.config['MAIL_PORT'] = 587
    app.config['MAIL_USE_TLS'] = True
    app.config['MAIL_USERNAME'] = 'pongw.2210@gmail.com'
    app.config['MAIL_PASSWORD'] = 'naok eohy xcrk qlup'
    app.config['MAIL_DEFAULT_SENDER'] = 'pongw.2210@gmail.com'

    db.init_app(app)
    from app import admin_view
    admin_view.init_admin(app)
    login.init_app(app)
    mail.init_app(app)
    login.login_view = "auth.login"

    # Đăng ký các blueprint
    from app.routes import auth
    app.register_blueprint(auth.auth_bp)

    from app.routes import events
    app.register_blueprint(events.events_bp)

    from app.routes import event_organizer
    app.register_blueprint(event_organizer.event_organizer_bp)

    from app.routes import admin
    app.register_blueprint(admin.admin_bp)



    return app
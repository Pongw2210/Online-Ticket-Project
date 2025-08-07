from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import cloudinary


db = SQLAlchemy()

def create_app():
    app = Flask(__name__)

    # App secret + Config DB
    app.secret_key = "%$@%^@%#^VGHGD"
    app.config["SQLALCHEMY_DATABASE_URI"] = "mysql+pymysql://root:12345@localhost/ticket_db?charset=utf8mb4"
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    # Cloudinary config
    cloudinary.config(
        cloud_name='dgqx9xde1',
        api_key='455275651816759',
        api_secret='4ouN8Z8Hjj1ahlD7lH8sU21MWwA'
    )

    db.init_app(app)

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

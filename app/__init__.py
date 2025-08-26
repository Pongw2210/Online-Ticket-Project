from flask import Flask
from flask_login import LoginManager
from flask_mail import Mail
import cloudinary

from app.extensions import db
from app.admin_view import flask_admin

login = LoginManager()
mail = Mail()


def create_app(config_class=None):
    app = Flask(__name__)


    if config_class:
        app.config.from_object(config_class)
    else:

        app.secret_key = "%$@%^@%#^VGHGD"
        app.config["SQLALCHEMY_DATABASE_URI"] = "mysql+pymysql://root:123456@localhost/ticket_db?charset=utf8mb4"
        app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

        # Cloudinary config
        cloudinary.config(
            cloud_name="dgqx9xde1",
            api_key="455275651816759",
            api_secret="4ouN8Z8Hjj1ahlD7lH8sU21MWwA",
        )

        # Mail config
        app.config["MAIL_SERVER"] = "smtp.gmail.com"
        app.config["MAIL_PORT"] = 587
        app.config["MAIL_USE_TLS"] = True
        app.config["MAIL_USERNAME"] = "pongw.2210@gmail.com"
        app.config["MAIL_PASSWORD"] = "naok eohy xcrk qlup"
        app.config["MAIL_DEFAULT_SENDER"] = "pongw.2210@gmail.com"


    db.init_app(app)
    login.init_app(app)
    mail.init_app(app)
    login.login_view = "auth.login"


    if not app.config.get("TESTING", False):
        from app import admin_view
        admin_view.init_admin(app)


    from app.routes import auth, events, event_organizer, admin
    app.register_blueprint(auth.auth_bp)
    app.register_blueprint(events.events_bp)
    app.register_blueprint(event_organizer.event_organizer_bp)
    app.register_blueprint(admin.admin_bp)

    from app.routes.report import report_bp
    app.register_blueprint(report_bp)

    return app

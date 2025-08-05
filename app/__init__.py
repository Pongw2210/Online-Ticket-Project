from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import json

db = SQLAlchemy()

def create_app():
    app = Flask(__name__)
    app.config.from_object("config.Config")

    db.init_app(app)

    # Custom filter để parse JSON
    @app.template_filter('from_json')
    def from_json_filter(value):
        if value:
            try:
                return json.loads(value)
            except:
                return []
        return []

    # Đăng ký các blueprint
    from app.routes import events
    app.register_blueprint(events.bp)

    from app.routes import auth           # 👈 Thêm dòng này
    app.register_blueprint(auth.auth_bp)  # 👈 Và dòng này

    return app

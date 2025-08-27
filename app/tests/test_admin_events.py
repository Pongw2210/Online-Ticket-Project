import pytest
from datetime import datetime, timedelta
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView

from app.data.models import Event, StatusEventEnum, EventFormatEnum, EventTypeEnum
from app.extensions import db  # db từ extensions

# -------------------------
# Fixture app và client
# -------------------------
@pytest.fixture
def app():
    app = Flask(__name__)
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    app.config['SECRET_KEY'] = 'test_secret'
    db.init_app(app)

    # Init Flask-Admin
    admin = Admin(app, name="Admin", template_mode="bootstrap4")
    admin.add_view(ModelView(Event, db.session, endpoint='events'))

    with app.app_context():
        db.create_all()
        yield app
        db.drop_all()


@pytest.fixture
def client(app):
    return app.test_client()


# -------------------------
# Test trang list events
# -------------------------
def test_events_page(client, app):
    # Tạo Event test
    with app.app_context():
        event = Event(
            name="Sự kiện test",
            status=StatusEventEnum.DANG_DUYET,
            event_format=EventFormatEnum.OFFLINE,
            event_type=EventTypeEnum.NHAC_SONG,
            start_datetime=datetime.utcnow(),
            end_datetime=datetime.utcnow() + timedelta(hours=2)
        )
        db.session.add(event)
        db.session.commit()

    # Truy cập URL list events Flask-Admin
    response = client.get('/admin/events/')
    assert response.status_code == 200
    # Kiểm tra event đã hiển thị
    assert "Sự kiện test" in response.get_data(as_text=True)


# -------------------------
# Test tạo Event mới
# -------------------------
def test_create_event(client, app):
    with app.app_context():
        event_count_before = Event.query.count()
        event = Event(
            name="Event mới",
            status=StatusEventEnum.DANG_DUYET,
            event_format=EventFormatEnum.OFFLINE,
            event_type=EventTypeEnum.NHAC_SONG,
            start_datetime=datetime.utcnow(),
            end_datetime=datetime.utcnow() + timedelta(hours=1)
        )
        db.session.add(event)
        db.session.commit()
        event_count_after = Event.query.count()
        assert event_count_after == event_count_before + 1

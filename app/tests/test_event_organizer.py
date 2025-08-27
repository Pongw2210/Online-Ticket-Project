import io
import json
import pytest
from datetime import datetime
from app import create_app, db
from app.data.models import (
    User, UserEnum, EventOrganizer, Event,
    EventFormatEnum, EventTypeEnum
)

# Config riêng cho test
class TestConfig:
    TESTING = True
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    WTF_CSRF_ENABLED = False
    SECRET_KEY = "test_secret"


@pytest.fixture
def app():
    app = create_app(TestConfig)   # truyền config test
    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def organizer_user(app):
    """Tạo 1 user có role = NGUOI_TO_CHUC"""
    with app.app_context():
        user = User(username="org", email="org@test.com", role=UserEnum.NGUOI_TO_CHUC)
        user.set_password("123456")
        db.session.add(user)
        db.session.flush()
        org = EventOrganizer(fullname="Organizer", gender="N/A", user_id=user.id)
        db.session.add(org)
        db.session.commit()
        db.session.refresh(user)   # tránh DetachedInstanceError
        return user


def login_as(client, user):
    """Fake login cho Flask-Login"""
    with client.session_transaction() as sess:
        sess["_user_id"] = str(user.id)


def test_create_event_api(client, app, organizer_user, monkeypatch):
    """Test API tạo event"""
    login_as(client, organizer_user)

    # fake upload cloudinary
    monkeypatch.setattr("cloudinary.uploader.upload", lambda _: {"secure_url": "http://fake.img"})

    data = {
        "name_event": "Test Event",
        "description": "Desc",
        "rules": "No rules",
        "performers": "Band",
        "organizer": "Org",
        "event_format": "online",
        "event_type": "NHAC_SONG",  # enum hợp lệ
        "start_time": datetime.now().isoformat(),
        "end_time": datetime.now().isoformat(),
        "tickets": json.dumps([{"name": "VIP", "price": 100, "quantity": 10, "benefits": "Test"}]),
        "livestream_url": "http://fake.stream"   #  thêm livestream_url cho event online
    }

    # fake file ảnh
    data["image"] = (io.BytesIO(b"fake image"), "test.png")

    resp = client.post("/organizer/api/create-event", data=data, content_type="multipart/form-data")
    assert resp.status_code == 200
    assert resp.get_json()["success"] is True


def test_hide_show_event_api(client, app, organizer_user):
    """Test API ẩn / hiện event"""
    login_as(client, organizer_user)

    with app.app_context():
        # merge user để còn session
        user = db.session.merge(organizer_user)

        ev = Event(
            name="EventHide",
            description="Desc",
            event_format=EventFormatEnum.ONLINE,
            event_type=EventTypeEnum.NHAC_SONG,
            start_datetime=datetime.now(),
            end_datetime=datetime.now(),
            organizer_id=user.event_organizer.id,
            image_url="img.png"
        )
        db.session.add(ev)
        db.session.commit()
        event_id = ev.id

    # hide
    r1 = client.post(f"/organizer/api/{event_id}/hide")
    assert r1.status_code == 200
    assert r1.get_json()["message"] == "Ẩn sự kiện thành công."

    # show
    r2 = client.post(f"/organizer/api/{event_id}/show")
    assert r2.status_code == 200
    assert r2.get_json()["message"] == "Công khai sự kiện thành công."


def test_delete_event_api(client, app, organizer_user):
    """Test API xóa event"""
    login_as(client, organizer_user)

    with app.app_context():
        #  merge user để còn session
        user = db.session.merge(organizer_user)

        ev = Event(
            name="EventDelete",
            description="Desc",
            event_format=EventFormatEnum.ONLINE,
            event_type=EventTypeEnum.NHAC_SONG,
            start_datetime=datetime.now(),
            end_datetime=datetime.now(),
            organizer_id=user.event_organizer.id,
            image_url="img.png"
        )
        db.session.add(ev)
        db.session.commit()
        event_id = ev.id

    r = client.delete(f"/organizer/api/{event_id}/delete")
    assert r.status_code == 200
    assert r.get_json()["message"] == "Xóa sự kiện thành công."

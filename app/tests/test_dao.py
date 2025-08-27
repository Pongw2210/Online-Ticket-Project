import pytest
import hashlib
import uuid
from datetime import datetime, timedelta

from app.extensions import db
from app.data.models import (
    User, UserEnum,
    Event, EventTypeEnum, EventFormatEnum, StatusEventEnum,
    TicketType
)
import app.dao as dao


@pytest.fixture
def sample_user(app):
    """Tạo user mẫu"""
    with app.app_context():
        unique = uuid.uuid4().hex[:6]
        user = User(
            username=f"user_{unique}",
            email=f"user_{unique}@example.com",
            role=UserEnum.ADMIN,
            password=hashlib.md5("123".encode("utf-8")).hexdigest()
        )
        db.session.add(user)
        db.session.commit()
        return user.id   # trả về id để tránh DetachedInstanceError


@pytest.fixture
def sample_event(app, sample_user):
    """Tạo event mẫu"""
    with app.app_context():
        event = Event(
            name="Music Night",
            start_datetime=datetime.utcnow(),
            end_datetime=datetime.utcnow() + timedelta(hours=2),
            event_format=EventFormatEnum.OFFLINE,   # ✅ sửa đúng enum
            event_type=EventTypeEnum.NHAC_SONG,
            organizer_id=sample_user,
            status=StatusEventEnum.DA_DUYET
        )
        db.session.add(event)
        db.session.commit()
        return event.id


def test_get_user_by_id(app, sample_user):
    with app.app_context():
        u = dao.get_user_by_id(sample_user)
        assert u is not None
        assert "user_" in u.username


def test_auth_user(app, sample_user):
    with app.app_context():
        real_user = dao.get_user_by_id(sample_user)
        u = dao.auth_user(real_user.username, "123", role=UserEnum.ADMIN)
        assert u is not None
        assert u.username == real_user.username

        # Sai password
        u2 = dao.auth_user(real_user.username, "wrong")
        assert u2 is None


def test_load_event_type_enum():
    enums = dao.load_event_type_enum()
    assert "NHAC_SONG" in enums
    assert enums["NHAC_SONG"] == EventTypeEnum.NHAC_SONG.value


def test_load_approved_events(app, sample_event, sample_user):
    with app.app_context():
        events = dao.load_approved_events(sample_user)
        assert len(events) == 1
        assert events[0].status == StatusEventEnum.DA_DUYET


def test_load_pending_events(app, sample_user, sample_event):
    with app.app_context():
        e = dao.get_event_by_id(sample_event)
        e.status = StatusEventEnum.DANG_DUYET
        db.session.commit()

        events = dao.load_pending_events(sample_user)
        assert len(events) == 1
        assert events[0].status == StatusEventEnum.DANG_DUYET


def test_load_rejected_events(app, sample_user, sample_event):
    with app.app_context():
        e = dao.get_event_by_id(sample_event)
        e.status = StatusEventEnum.TU_CHOI
        db.session.commit()

        events = dao.load_rejected_events(sample_user)
        assert len(events) == 1
        assert events[0].status == StatusEventEnum.TU_CHOI


def test_load_hidden_events(app, sample_user, sample_event):
    with app.app_context():
        e = dao.get_event_by_id(sample_event)
        e.status = StatusEventEnum.DA_AN
        db.session.commit()

        events = dao.load_hidden_events(sample_user)
        assert len(events) == 1
        assert events[0].status == StatusEventEnum.DA_AN


def test_get_event_by_id(app, sample_event):
    with app.app_context():
        e = dao.get_event_by_id(sample_event)
        assert e is not None
        assert e.name == "Music Night"


def test_load_ticket_type(app, sample_event):
    with app.app_context():
        ticket = TicketType(
            event_id=sample_event,
            name="VIP",
            price=100,
            quantity=50
        )
        db.session.add(ticket)
        db.session.commit()

        tickets = dao.load_ticket_type(sample_event)
        assert len(tickets) == 1
        assert tickets[0].name == "VIP"

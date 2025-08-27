import pytest
import uuid
from datetime import datetime, timedelta

from app.data.models import User, UserEnum, Event, EventTypeEnum, Booking, EventFormatEnum
from app.extensions import db
from app.admin_view import init_admin


@pytest.fixture(scope="session", autouse=True)
def setup_admin(app):
    """Gắn admin vào app giống production (chỉ init một lần cho cả session)"""
    with app.app_context():
        init_admin(app)
    yield


@pytest.fixture
def sample_data(app):
    """Tạo dữ liệu mẫu để test giao diện Admin"""
    with app.app_context():
        unique = str(uuid.uuid4())[:6]

        user = User(
            username=f"user_{unique}",
            email=f"user_{unique}@example.com",
            role=UserEnum.ADMIN,
        )
        user.set_password("123")
        db.session.add(user)
        db.session.commit()

        event = Event(
            name=f"Event {unique}",
            start_datetime=datetime.utcnow(),
            end_datetime=datetime.utcnow() + timedelta(hours=2),
            event_format=EventFormatEnum.OFFLINE,
            event_type=EventTypeEnum.NHAC_SONG,
            organizer_id=None,
        )
        db.session.add(event)
        db.session.commit()

        booking = Booking(
            user_id=user.id,
            event_id=event.id,
            total_price=500,
            booking_date=datetime.utcnow(),
        )
        db.session.add(booking)
        db.session.commit()

        return {"user": user, "event": event, "booking": booking}


def test_admin_index_html(client, sample_data):
    """Trang /admin/ trả về 200 và có thống kê"""
    resp = client.get("/admin/")
    assert resp.status_code == 200

    html = resp.get_data(as_text=True)
    # Kiểm tra tiêu đề và một số thống kê mặc định trong dashboard
    assert "Ticket Admin" in html
    assert "User" in html
    assert "Booking" in html
    # Dashboard có thể hiển thị Event Organizer hoặc Event Online/Offline
    assert "Event Organizer" in html or "Event Online" in html or "Event Offline" in html
    # Kiểm tra link menu
    assert "Duyệt sự kiện" in html
    assert "Đăng xuất" in html


def test_admin_index_no_data(client):
    """Trang /admin/ vẫn load được khi DB rỗng"""
    resp = client.get("/admin/")
    assert resp.status_code == 200

    html = resp.get_data(as_text=True)
    assert "User" in html
    assert "Booking" in html
    assert "Event Organizer" in html or "Event Online" in html or "Event Offline" in html

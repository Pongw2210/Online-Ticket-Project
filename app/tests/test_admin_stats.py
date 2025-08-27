import pytest
import uuid
from datetime import datetime, timedelta

from flask_admin import Admin
from app.extensions import db
from app.admin_stats import StatsView
from app.data.models import User, UserEnum, Event, EventTypeEnum, Booking, EventFormatEnum


@pytest.fixture(autouse=True)
def setup_statsview(app):
    """Thêm StatsView vào Flask-Admin có sẵn"""
    # Tìm admin đã được init trong app
    admin = None
    for ext in app.extensions.get("admin", []):
        if isinstance(ext, Admin):
            admin = ext
            break
    if admin is None:
        admin = Admin(app, url="/admin", template_mode="bootstrap4")

    # Thêm StatsView nếu chưa có
    found = any(isinstance(v, StatsView) for v in admin._views)
    if not found:
        admin.add_view(StatsView(name="Stats", endpoint="stats"))
    yield


@pytest.fixture
def sample_data(app):
    with app.app_context():
        unique = str(uuid.uuid4())[:8]

        user1 = User(
            username=f"u1_{unique}",
            email=f"u1_{unique}@example.com",
            role=UserEnum.ADMIN,
        )
        user1.set_password("123")
        db.session.add(user1)
        db.session.commit()

        event1 = Event(
            name=f"Event 1 {unique}",
            start_datetime=datetime.utcnow(),
            end_datetime=datetime.utcnow() + timedelta(hours=2),
            event_format=EventFormatEnum.OFFLINE,
            event_type=EventTypeEnum.NHAC_SONG,
            organizer_id=None,
        )
        db.session.add(event1)
        db.session.commit()

        booking1 = Booking(
            user_id=user1.id,
            event_id=event1.id,
            total_price=200,
            booking_date=datetime.utcnow(),
        )
        db.session.add(booking1)
        db.session.commit()

        return {"user": user1, "event": event1, "booking": booking1}


def test_stats_index_html(client, sample_data):
    resp = client.get("/admin/stats/")
    assert resp.status_code == 200
    text = resp.get_data(as_text=True)

    # Kiểm tra tiếng Việt trong giao diện render
    assert "Thống Kê" in text
    assert "Tổng sự kiện" in text
    assert "Tổng người dùng" in text
    assert "Doanh thu" in text


def test_stats_export_csv(client, sample_data):
    resp = client.get("/admin/stats/?export=csv")
    assert resp.status_code == 200
    assert resp.mimetype == "text/csv"
    csv_text = resp.get_data(as_text=True)

    assert "Summary" in csv_text
    assert "Total events" in csv_text
    assert "Top 5 events" in csv_text
    assert "Top 5 users" in csv_text

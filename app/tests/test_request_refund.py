import pytest
from datetime import datetime
from app.data.models import (
    User, EventOrganizer, Event, TicketType, Booking, BookingDetail,
    StatusBookingEnum, EventFormatEnum, EventTypeEnum
)

@pytest.fixture
def paid_booking(db_session):
    # 1. Tạo User
    user = User(
        username="testuser",
        email="test@example.com",
        password="123"
    )
    user.set_password("123")
    db_session.add(user)
    db_session.commit()

    # 2. Tạo EventOrganizer
    organizer = EventOrganizer(
        fullname="Test Organizer",
        email="org@example.com",
        gender="Nam"
    )
    db_session.add(organizer)
    db_session.commit()

    # 3. Tạo Event
    event = Event(
        name="Test Event",
        start_datetime=datetime.utcnow(),
        end_datetime=datetime.utcnow(),
        event_format=EventFormatEnum.OFFLINE,
        event_type=EventTypeEnum.NHAC_SONG,
        organizer_id=organizer.id
    )
    db_session.add(event)
    db_session.commit()

    # 4. Tạo TicketType
    ticket = TicketType(
        name="VIP",
        price=100,
        quantity=10,
        event_id=event.id
    )
    db_session.add(ticket)
    db_session.commit()

    # 5. Tạo Booking và BookingDetail
    booking = Booking(
        user_id=user.id,
        event_id=event.id,
        total_price=100,
        status=StatusBookingEnum.DA_THANH_TOAN
    )
    db_session.add(booking)
    db_session.commit()

    booking_detail = BookingDetail(
        booking_id=booking.id,
        ticket_type_id=ticket.id,
        quantity=1,
        unit_price=ticket.price
    )
    db_session.add(booking_detail)
    db_session.commit()

    return {
        "user": user,
        "organizer": organizer,
        "event": event,
        "ticket": ticket,
        "booking": booking,
        "booking_detail": booking_detail
    }

# =========================
# Các test cơ bản
# =========================

def test_booking_total_price(paid_booking):
    booking = paid_booking["booking"]
    assert booking.total_price == 100

def test_booking_status_paid(paid_booking):
    booking = paid_booking["booking"]
    assert booking.status == StatusBookingEnum.DA_THANH_TOAN

def test_ticket_quantity(paid_booking):
    ticket = paid_booking["ticket"]
    assert ticket.quantity == 10

def test_user_created(paid_booking):
    user = paid_booking["user"]
    assert user.username == "testuser"

def test_booking_detail_linked(paid_booking):
    booking_detail = paid_booking["booking_detail"]
    booking = paid_booking["booking"]
    ticket = paid_booking["ticket"]
    assert booking_detail.booking_id == booking.id
    assert booking_detail.ticket_type_id == ticket.id
    assert booking_detail.quantity == 1
    assert booking_detail.unit_price == ticket.price

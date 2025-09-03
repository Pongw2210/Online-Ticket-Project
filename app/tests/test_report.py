import pytest
from datetime import datetime, date
from app.data.models import (
    User, Customer, EventOrganizer, Event, TicketType, Booking, BookingDetail,
    StatusBookingEnum, EventFormatEnum, EventTypeEnum
)

# ----------------- Fixture cho dữ liệu -----------------
@pytest.fixture
def organizer_setup(db_session, app):
    with app.app_context():
        # Tạo organizer user
        organizer_user = User(username="orguser", email="org@example.com")
        organizer_user.set_password("123")
        db_session.add(organizer_user)
        db_session.commit()

        organizer = EventOrganizer(
            fullname="Org 1", email="org@example.com", gender="Nam", user_id=organizer_user.id
        )
        db_session.add(organizer)
        db_session.commit()

        # Tạo Event
        event = Event(
            name="Event 1",
            start_datetime=datetime.utcnow(),
            end_datetime=datetime.utcnow(),
            event_format=EventFormatEnum.OFFLINE,
            event_type=EventTypeEnum.NHAC_SONG,
            organizer_id=organizer.id
        )
        db_session.add(event)
        db_session.commit()

        # TicketType
        ticket = TicketType(name="VIP", price=100, quantity=10, event_id=event.id)
        db_session.add(ticket)
        db_session.commit()

        # Customer user
        customer_user = User(username="cust1", email="cust@example.com")
        customer_user.set_password("123")
        db_session.add(customer_user)
        db_session.commit()

        # Customer
        customer = Customer(
            fullname="Customer 1",
            email="cust1@example.com",
            gender="Nam",
            dob= date(2000, 1, 1),
            number_phone="0123456789",
            user_id=customer_user.id
        )
        db_session.add(customer)
        db_session.commit()

        # Booking
        booking = Booking(
            user_id=customer_user.id,
            event_id=event.id,
            total_price=100,
            final_price=100,
            status=StatusBookingEnum.DA_THANH_TOAN
        )
        db_session.add(booking)
        db_session.commit()

        # BookingDetail
        booking_detail = BookingDetail(
            booking_id=booking.id,
            ticket_type_id=ticket.id,
            quantity=1,
            unit_price=ticket.price
        )
        db_session.add(booking_detail)
        db_session.commit()

        return {
            "organizer_user": organizer_user,
            "organizer": organizer,
            "event": event,
            "ticket": ticket,
            "customer_user": customer_user,
            "customer": customer,
            "booking": booking,
            "booking_detail": booking_detail
        }

# ----------------- Helper login -----------------
def login_client(client, user):
    """Login bằng cách set session trực tiếp, không dùng login_user()"""
    with client.session_transaction() as sess:
        sess["_user_id"] = str(user.id)
        sess["_fresh"] = True

# ----------------- Test API summary -----------------
def test_api_summary(client, organizer_setup):
    login_client(client, organizer_setup["organizer_user"])
    resp = client.get("/organizer/report/api/summary")
    assert resp.status_code == 200
    data = resp.get_json()
    assert "total_revenue" in data
    assert "total_tickets" in data
    assert data["total_revenue"] == 100
    assert data["total_tickets"] == 1

# ----------------- Test API revenue_by_ticket -----------------
def test_api_revenue_by_ticket(client, organizer_setup):
    login_client(client, organizer_setup["organizer_user"])
    resp = client.get("/organizer/report/api/revenue_by_ticket")
    assert resp.status_code == 200
    data = resp.get_json()
    assert data["labels"] == ["VIP"]
    assert data["values"] == [100]

# ----------------- Test API top_customers -----------------
def test_api_top_customers(client, organizer_setup):
    login_client(client, organizer_setup["organizer_user"])
    resp = client.get("/organizer/report/api/top_customers")
    assert resp.status_code == 200
    data = resp.get_json()
    assert len(data["rows"]) == 1
    row = data["rows"][0]
    assert row["name"] == "Customer 1"
    assert row["tickets"] == 1
    assert row["spent"] == 100.0

# ----------------- Test CSV export -----------------
def test_export_top_customers_csv(client, organizer_setup):
    login_client(client, organizer_setup["organizer_user"])
    resp = client.get("/organizer/report/export/top_customers.csv")
    assert resp.status_code == 200
    assert resp.mimetype == "text/csv"
    text = resp.get_data(as_text=True)
    assert "Khach hang,Sove,Doanhthu" in text
    assert "Customer 1,1,100" in text

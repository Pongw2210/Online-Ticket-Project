import unittest
from datetime import datetime
from app.extensions import db
from app.data.models import (
    User, Customer, EventOrganizer, Admin,
    Event, TicketType, Booking, BookingDetail, Seat, BookingSeat,
    UserEnum, EventFormatEnum, EventTypeEnum, StatusBookingEnum, StatusSeatEnum
)
from app import create_app

class TestModels(unittest.TestCase):
    def setUp(self):
        """Thiết lập môi trường test"""
        self.app = create_app()
        self.app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        self.app.config['TESTING'] = True
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()

        # Tạo dữ liệu mẫu
        self.user = User(username="testuser", email="test@example.com")
        self.user.set_password("123456")
        db.session.add(self.user)
        db.session.commit()

    def tearDown(self):
        """Dọn dẹp sau mỗi test"""
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_user_password(self):
        """Kiểm tra hash và check password"""
        user = User.query.first()
        self.assertTrue(user.check_password("123456"))
        self.assertFalse(user.check_password("wrong"))

    def test_user_fullname_property(self):
        """Kiểm tra fullname trả về theo role"""
        customer = Customer(fullname="Nguyen Van A", email="a@example.com",
                            gender="Nam", dob=datetime(2000,1,1), number_phone="0123456789",
                            user_id=self.user.id)
        db.session.add(customer)
        db.session.commit()
        self.user.role = UserEnum.KHACH_HANG
        db.session.commit()
        self.assertEqual(self.user.fullname, "Nguyen Van A")

    def test_create_event_ticket(self):
        """Tạo event và ticket"""
        organizer = EventOrganizer(fullname="Org A", email="org@example.com",
                                   gender="Nu", user_id=self.user.id)
        db.session.add(organizer)
        db.session.commit()

        event = Event(name="Event 1", event_format=EventFormatEnum.OFFLINE,
                      event_type=EventTypeEnum.NHAC_SONG, start_datetime=datetime.utcnow(),
                      end_datetime=datetime.utcnow(), organizer_id=organizer.id)
        db.session.add(event)
        db.session.commit()

        ticket = TicketType(name="VIP", price=100.0, quantity=50, event_id=event.id)
        db.session.add(ticket)
        db.session.commit()

        self.assertEqual(ticket.event.name, "Event 1")
        self.assertEqual(len(event.ticket_types), 1)

    def test_booking_seat(self):
        """Test đặt vé và ghế"""
        event = Event(name="Event Seat", event_format=EventFormatEnum.OFFLINE,
                      event_type=EventTypeEnum.NHAC_SONG, start_datetime=datetime.utcnow(),
                      end_datetime=datetime.utcnow())
        db.session.add(event)
        db.session.commit()

        seat1 = Seat(event_id=event.id, seat_code="A1")
        seat2 = Seat(event_id=event.id, seat_code="A2")
        db.session.add_all([seat1, seat2])
        db.session.commit()

        booking = Booking(user_id=self.user.id, event_id=event.id, total_price=200, status=StatusBookingEnum.CHO_THANH_TOAN)
        db.session.add(booking)
        db.session.commit()

        bs1 = BookingSeat(booking_id=booking.id, seat_id=seat1.id)
        db.session.add(bs1)
        db.session.commit()

        self.assertEqual(bs1.seat.seat_code, "A1")
        self.assertEqual(bs1.booking.total_price, 200)

if __name__ == '__main__':
    unittest.main()

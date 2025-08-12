from datetime import datetime
from sqlalchemy.orm import relationship
from app import db
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Enum, Text, Time, Float, Boolean
from enum import Enum as RoleEnum
from flask_login import UserMixin
import enum
import hashlib

class UserEnum(RoleEnum):
    KHACH_HANG = "Khách hàng "
    NGUOI_TO_CHUC = "Người tổ chức"
    ADMIN = "Người quản trị"

class StatusEventEnum(RoleEnum):
    DA_DUYET = "Đã duyệt "
    DANG_DUYET = "Đang duyệt"
    TU_CHOI = "Từ chối"
    DA_AN = "Đã ẩn "

class StatusBookingEnum(RoleEnum):
    CHO_THANH_TOAN = "Chờ thanh toán"
    DA_THANH_TOAN = "Đã thanh toán"
    DA_HUY = "Đã hủy"

class StatusSeatEnum(RoleEnum):
    TRONG = "Trống"
    DA_DAT = "Đã đặt"

class EventFormatEnum(RoleEnum):
    ONLINE ="Trực tuyến"
    OFFLINE = "Trực tiếp"

class EventTypeEnum(RoleEnum):
    NHAC_SONG = "Nhạc sống"
    NGHE_THUAT = "Sân khấu & Nghệ thuật"
    THE_THAO = "Thể thao"
    KHAC = "Khác"

class Base(db.Model):
    __abstract__ = True
    id = Column(Integer, primary_key=True, autoincrement=True)
    __table_args__ = {'extend_existing': True}

class Customer(Base):
    __tablename__ = 'customer'
    fullname = Column(String(100),nullable=False)
    email = Column(String(100), nullable=False)
    gender = Column(String(10), nullable=False)
    dob = Column(DateTime, nullable=False)
    number_phone = Column(String(10), nullable=False)
    user_id = Column(Integer,ForeignKey('user.id'),nullable=False)

class EventOrganizer(Base):
    __tablename__ = 'event_organizer'
    fullname = Column(String(100), nullable=False)
    email = Column(String(100), nullable=True)
    gender = Column(String(10), nullable=False)
    user_id = Column(Integer, ForeignKey('user.id'), nullable=True)

class Admin(Base):
    __tablename__ = 'admin'
    fullname = Column(String(100), nullable=False)
    email = Column(String(100), nullable=True)
    gender = Column(String(10), nullable=False)
    user_id = Column(Integer, ForeignKey('user.id'), nullable=True)

class User(Base,UserMixin):
    __tablename__ = 'user'
    username = Column(String(50),unique=True,nullable=False)
    email = Column(String(100), unique=True, nullable=False)
    password = Column(String(50),nullable=False)
    avatar = Column(String(300),default="https://res.cloudinary.com/dgqx9xde1/image/upload/v1744899995/User1_cmpdyi.jpg")
    role = Column(Enum(UserEnum), default=UserEnum.KHACH_HANG)
    joined_date = Column(DateTime, default=datetime.utcnow)
    customer = relationship(Customer, uselist=False, backref="user", cascade="all, delete")
    event_organizer = relationship(EventOrganizer, uselist=False, backref="user", cascade="all, delete")
    admin = relationship(Admin, uselist=False, backref="user", cascade="all, delete")

    def set_password(self, password):
        """Hash password và lưu vào database"""
        self.password = hashlib.md5(password.encode('utf-8')).hexdigest()

    def check_password(self, password):
        """Kiểm tra password có đúng không"""
        return self.password == hashlib.md5(password.encode('utf-8')).hexdigest()

    @property
    def fullname(self):
        if self.role == UserEnum.KHACH_HANG and self.customer:
            return self.customer.fullname
        elif self.role == UserEnum.NGUOI_TO_CHUC and self.event_organizer:
            return self.event_organizer.fullname
        elif self.role == UserEnum.ADMIN and self.admin:
            return self.admin.fullname
        return self.username

class TicketType(Base):
    __tablename__ = 'ticket_type'
    name = Column(String(50))
    price = Column(Float)
    quantity = Column(Integer, nullable= False)
    benefits = Column(Text)
    event_id = Column(Integer, ForeignKey("event.id"), nullable=False)
    requires_seat = Column(Boolean, default=False)   #thể hiện loại vé có được chọn ghế hay ngồi ngẫu nhiên

    @property
    def benefits_list(self):
        return [b.strip() for b in self.benefits.split('|')] if self.benefits else []

class EventOffline(Base):
    __tablename__ = 'event_offline'
    venue_name = Column(String(255), nullable=False)
    location = Column(String(255), nullable=False)
    has_seat = Column(Boolean, default=False)
    event_id = Column(Integer, ForeignKey('event.id'), nullable=False,unique=True)

class EventOnline(Base):
    __tablename__ = 'event_online'
    livestream_url = Column(String(255), nullable=False)
    event_id = Column(Integer, ForeignKey('event.id'), nullable=False, unique=True)

class Event(Base):
    __tablename__ = 'event'
    name = Column(String(255), nullable=False)
    description = Column(Text)
    start_datetime = Column(DateTime, nullable=False)
    end_datetime = Column(DateTime, nullable=False)
    rules = Column(Text)
    authors = Column(Text)
    producers = Column(Text)
    image_url = Column(String(255))
    status = Column(Enum(StatusEventEnum), default=StatusEventEnum.DANG_DUYET)
    event_format = Column(Enum(EventFormatEnum), nullable=False)
    event_type = Column(Enum(EventTypeEnum), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    organizer_id = Column(Integer, ForeignKey('event_organizer.id'))
    event_organizer = relationship("EventOrganizer", backref="events")

    ticket_types = relationship("TicketType", backref="event", cascade="all, delete")
    event_offline = relationship(EventOffline, uselist=False, backref="event", cascade="all, delete")
    event_online = relationship(EventOnline, uselist=False, backref="event", cascade="all, delete")

    # Thêm quan hệ với bảng ghi lý do từ chối
    rejection_logs = relationship("EventRejectionLog", backref="event", cascade="all, delete")

class EventRejectionLog(Base):
    __tablename__ = 'event_rejection_log'

    event_id = Column(Integer, ForeignKey('event.id'), nullable=False)
    reason = Column(Text, nullable=False)
    rejected_at = Column(DateTime, default=datetime.utcnow)

class Booking(Base):
    __tablename__ = 'booking'

    user_id = Column(Integer, ForeignKey('user.id'), nullable=False)
    event_id = Column(Integer, ForeignKey('event.id'), nullable=False)
    total_price = Column(Float, nullable=False)
    booking_date = Column(DateTime, default=datetime.utcnow)
    status = Column(Enum(StatusBookingEnum), default=StatusBookingEnum.CHO_THANH_TOAN)

    user = relationship("User", backref="bookings")
    event = relationship("Event", backref="bookings")
    booking_seats = relationship("BookingSeat", back_populates="booking", cascade="all, delete")
    booking_details = relationship("BookingDetail", backref="booking", cascade="all, delete")

class BookingDetail(Base):
    __tablename__ = 'booking_detail'

    booking_id = Column(Integer, ForeignKey('booking.id'))
    ticket_type_id = Column(Integer, ForeignKey('ticket_type.id'))
    quantity = Column(Integer, nullable=False)
    unit_price = Column(Float, nullable=False)

    ticket_type = relationship("TicketType")

class Seat(Base):
    __tablename__ = 'seat'

    event_id = Column(Integer, ForeignKey('event.id'), nullable=False)
    seat_code = Column(String(10), nullable=False)  # VD: "A1", "B3"
    status = Column(String(20), default="available")  # trạng thái: available, booked, etc.

    event = relationship("Event", backref="seats")

class BookingSeat(Base):
    __tablename__ = 'booking_seat'

    id = Column(Integer, primary_key=True, autoincrement=True)
    booking_id = Column(Integer, ForeignKey('booking.id'), nullable=False)
    seat_id = Column(Integer, ForeignKey('seat.id'), nullable=False)

    booking = relationship("Booking", back_populates="booking_seats")
    seat = relationship("Seat")
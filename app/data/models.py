from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Enum, Text, Float, Boolean
from enum import Enum as RoleEnum
from flask_login import UserMixin
import hashlib
from app.extensions import db
from sqlalchemy.orm import relationship, backref

class UserEnum(RoleEnum):
    KHACH_HANG = "Khách hàng"
    NGUOI_TO_CHUC = "Người tổ chức"
    ADMIN = "Người quản trị"

class StatusEventEnum(RoleEnum):
    DA_DUYET = "Đã duyệt"
    DANG_DUYET = "Đang duyệt"
    TU_CHOI = "Từ chối"
    DA_AN = "Đã ẩn"

class StatusBookingEnum(RoleEnum):
    CHO_THANH_TOAN = "Chờ thanh toán"
    DA_THANH_TOAN = "Đã thanh toán"
    DA_HUY = "Đã hủy"
    DA_HOAN = "Đã hoàn"

class StatusSeatEnum(RoleEnum):
    TRONG = "Trống"
    DA_DAT = "Đã đặt"

class EventFormatEnum(RoleEnum):
    ONLINE = "Trực tuyến"
    OFFLINE = "Trực tiếp"

class EventTypeEnum(RoleEnum):
    NHAC_SONG = "Nhạc sống"
    NGHE_THUAT = "Sân khấu & Nghệ thuật"
    THE_THAO = "Thể thao"
    KHAC = "Khác"

class DiscountTypeEnum(RoleEnum):
    PHAN_TRAM = "Phần trăm"
    SO_TIEN = "Số tiền"

class RefundStatusEnum(RoleEnum):
    CHO_XU_LY = "Chờ xử lý"
    DONG_Y = "Đồng ý hoàn"
    TU_CHOI = "Từ chối"

class Base(db.Model):
    __abstract__ = True
    id = Column(Integer, primary_key=True, autoincrement=True)
    __table_args__ = {'extend_existing': True}

class Customer(Base):
    __tablename__ = 'customer'

    fullname = Column(String(100), nullable=False)
    email = Column(String(100), nullable=False)
    gender = Column(String(10), nullable=False)
    dob = Column(DateTime, nullable=False)
    number_phone = Column(String(10), nullable=False)
    user_id = Column(Integer, ForeignKey('user.id'), nullable=False)

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

class User(Base, UserMixin):
    __tablename__ = 'user'

    username = Column(String(50), unique=True, nullable=False)
    email = Column(String(100), unique=True, nullable=False)
    password = Column(String(50), nullable=False)
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

class TicketVoucher(Base):
    __tablename__ = 'ticket_voucher'

    voucher_id = Column(Integer, ForeignKey("voucher.id"))
    ticket_type_id = Column(Integer, ForeignKey("ticket_type.id"))

class TicketType(Base):
    __tablename__ = 'ticket_type'

    name = Column(String(50))
    price = Column(Float)
    quantity = Column(Integer, nullable=False)
    benefits = Column(Text)
    event_id = Column(Integer, ForeignKey("event.id"), nullable=False)
    requires_seat = Column(Boolean, default=False)

    vouchers = relationship(TicketVoucher, backref="ticket_type", lazy=True)

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
    rejection_logs = relationship("EventRejectionLog", backref="event", cascade="all, delete")
    seats = relationship("Seat", backref="event", cascade="all, delete")
    vouchers = relationship("Voucher", backref="event", cascade="all, delete")

    @property
    def ticket_count(self):
        """Tổng số vé đã bán"""
        return sum(b.quantity for b in self.bookings)

    @property
    def revenue(self):
        """Tổng doanh thu"""
        return sum(b.total_price for b in self.bookings)

    @property
    def bookings_count(self):
        """Số lượt đặt vé"""
        return len(self.bookings)

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
    final_price = Column(Float, nullable=False)  # số tiền thực khách phải trả
    booking_date = Column(DateTime, default=datetime.utcnow)
    status = Column(Enum(StatusBookingEnum), default=StatusBookingEnum.CHO_THANH_TOAN)
    # created_at = Column(DateTime, default=datetime.utcnow)

    # Quan hệ
    user = relationship("User", backref="bookings")
    event = relationship("Event", backref="bookings")
    booking_details = relationship("BookingDetail", backref="booking", cascade="all, delete")
    booking_vouchers = relationship("BookingVoucher", backref="booking", cascade="all, delete")

class BookingDetail(Base):
    __tablename__ = 'booking_detail'

    booking_id = Column(Integer, ForeignKey('booking.id'))
    ticket_type_id = Column(Integer, ForeignKey('ticket_type.id'))
    quantity = Column(Integer, nullable=False)
    unit_price = Column(Float, nullable=False)
    qr_code_data = Column(Text, nullable=True)
    check_in = Column(Boolean,default=False)
    check_in_at = Column(DateTime)

    ticket_type = relationship("TicketType")
    booking_seats = relationship("BookingSeat", back_populates="booking_detail",cascade="all, delete")

class Seat(Base):
    __tablename__ = 'seat'

    event_id = Column(Integer, ForeignKey('event.id'), nullable=False)
    seat_code = Column(String(10), nullable=False)
    status = Column(Enum(StatusSeatEnum), default= StatusSeatEnum.TRONG)

class BookingSeat(Base):
    __tablename__ = 'booking_seat'

    booking_detail_id = Column(Integer, ForeignKey('booking_detail.id'), nullable=False)
    seat_id = Column(Integer, ForeignKey('seat.id'), nullable=False)

    booking_detail = relationship("BookingDetail", back_populates="booking_seats")
    seat = relationship("Seat")

class Voucher(Base):
    __tablename__ = 'voucher'

    code = Column(String(50), unique=True, nullable=False)
    discount_type = Column(Enum(DiscountTypeEnum), nullable=False)
    discount_value = Column(Float, nullable=False)
    quantity = Column(Integer, nullable=False, default=1)
    start_date = Column(DateTime, nullable=False)
    end_date = Column(DateTime, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    apply_all =  Column(Boolean, default=False)
    event_id = Column(Integer, ForeignKey('event.id'), nullable=False)

    ticket_vouchers = relationship("TicketVoucher", backref="voucher", lazy=True)

class BookingVoucher(Base):
    __tablename__='booking_voucher'

    booking_id = Column(Integer, ForeignKey('booking.id'), nullable=False)
    voucher_id = Column(Integer, ForeignKey('voucher.id'), nullable=False)

    voucher = relationship("Voucher")

class RefundRequest(Base):
    __tablename__ = 'refund_request'

    id = Column(Integer, primary_key=True, autoincrement=True)
    booking_detail_id = Column(Integer, ForeignKey('booking_detail.id'), nullable=False)
    reason = Column(Text, nullable=False)
    status = Column(Enum(RefundStatusEnum), default=RefundStatusEnum.CHO_XU_LY, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    booking_detail = relationship("BookingDetail", backref=backref("refund_request", uselist=False))

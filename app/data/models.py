from datetime import datetime
from sqlalchemy.orm import relationship
from app import db
from sqlalchemy import Column, Integer,String,DateTime,ForeignKey,Enum,Text,Time
from enum import Enum as RoleEnum
from flask_login import UserMixin

class UserEnum(RoleEnum):
    KHACH_HANG = "Khách hàng "
    NGUOI_TO_CHUC = "Người tổ chức"
    ADMIN = "Người quản trị"

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

class User(Base, UserMixin):
    __tablename__ = 'user'
    username = Column(String(50),unique=True,nullable=False)
    password = Column(String(50),nullable=False)
    avatar = Column(String(300),default="https://res.cloudinary.com/dgqx9xde1/image/upload/v1744899995/User1_cmpdyi.jpg")
    role = Column(Enum(UserEnum), default=UserEnum.KHACH_HANG)
    joined_date = Column(DateTime, default=datetime.utcnow)
    customer = relationship(Customer, uselist=False, backref="user", cascade="all, delete")
    event_organizer = relationship(EventOrganizer, uselist=False, backref="user", cascade="all, delete")
    admin = relationship(Admin, uselist=False, backref="user", cascade="all, delete")

class TicketType(Base):
    __tablename__ = 'ticket_type'
    name = db.Column(db.String(50))
    price = db.Column(db.Float)
    event_id = db.Column(db.Integer, db.ForeignKey("event_offline.id"), nullable=False)

class EventOffline(Base):
    __tablename__ = 'event_offline'
    name = Column(String(255), nullable=False)
    description = Column(Text)
    start_datetime = Column(DateTime, nullable=False)
    end_datetime = Column(DateTime, nullable=False)
    venue_name = Column(String(255), nullable=False)
    location = Column(String(255),nullable= False)
    rules = Column(Text)
    authors = Column(Text)
    producers = Column(Text)
    image_url = Column(String(255))

    ticket_types = db.relationship(TicketType, backref="event", lazy=True)

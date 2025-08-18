import hashlib
from app.data.models import User, EventTypeEnum, Event, StatusEventEnum, TicketType,Booking
from app import db
from sqlalchemy import func


def get_user_by_id(user_id):
    return User.query.get(user_id)

def auth_user(username,password,role=None):
    hashed_password = hashlib.md5(password.encode('utf-8')).hexdigest()

    query = User.query.filter(
        User.username == username,
        User.password == hashed_password
    )

    if role:
        query = query.filter(User.role == role)

    return query.first()

def load_event_type_enum():
    return {
        etype.name: etype.value
        for etype in EventTypeEnum
    }

def load_approved_events(organizer_id, search_query=None):
    query = Event.query.filter(
        Event.organizer_id == organizer_id,
        Event.status == StatusEventEnum.DA_DUYET
    )
    if search_query:
        query = query.filter(Event.name.ilike(f"%{search_query}%"))
    return query.all()


def load_pending_events(organizer_id, search_query=None):
    query = Event.query.filter_by(
        organizer_id=organizer_id,
        status=StatusEventEnum.DANG_DUYET
    )
    if search_query:
        query = query.filter(Event.name.ilike(f"%{search_query}%"))
    return query.all()


def load_rejected_events(organizer_id, search_query=None):
    query = Event.query.filter(
        Event.organizer_id == organizer_id,
        Event.status == StatusEventEnum.TU_CHOI
    )
    if search_query:
        query = query.filter(Event.name.ilike(f"%{search_query}%"))
    return query.all()


def load_hidden_events(organizer_id, search_query=None):
    query = Event.query.filter(
        Event.organizer_id == organizer_id,
        Event.status == StatusEventEnum.DA_AN
    )
    if search_query:
        query = query.filter(Event.name.ilike(f"%{search_query}%"))
    return query.all()


def get_event_by_id(event_id):
    return Event.query.get(event_id)

def load_ticket_type(event_id):
    ticket_types = TicketType.query.filter_by(event_id=event_id).all()
    return ticket_types

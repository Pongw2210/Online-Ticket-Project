import hashlib
from app.data.models import User,EventTypeEnum,Event,StatusEventEnum

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

def load_approved_events(organizer_id):
    events = Event.query.filter(
        Event.organizer_id == organizer_id,
        Event.status == StatusEventEnum.DA_DUYET
    )
    return events.all()

def load_pending_events(organizer_id):
    return Event.query.filter_by(
        organizer_id=organizer_id,
        status=StatusEventEnum.DANG_DUYET
    ).all()

def load_rejected_events (organizer_id):
    events = Event.query.filter(
        Event.organizer_id == organizer_id,
        Event.status == StatusEventEnum.TU_CHOI)

    return events.all()

def load_hidden_events (organizer_id):
    events = Event.query.filter(
        Event.organizer_id == organizer_id,
        Event.status == StatusEventEnum.DA_AN)

    return events.all()

def get_event_by_id(event_id):
    return Event.query.get(event_id)

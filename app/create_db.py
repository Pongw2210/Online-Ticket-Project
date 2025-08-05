from app import create_app, db
from app.models import Event, TicketType, Booking

app = create_app()
with app.app_context():
    db.create_all()

    # Thêm dữ liệu mẫu
    event1 = Event(name="V Concert", description="Đại nhạc hội hoành tráng", date="09-08-2025", location="Hà Nội")
    db.session.add(event1)
    db.session.commit()

    ticket1 = TicketType(name="Thường", price=250000, event_id=event1.id)
    ticket2 = TicketType(name="VIP", price=600000, event_id=event1.id)
    db.session.add_all([ticket1, ticket2])
    db.session.commit()

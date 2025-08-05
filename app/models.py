from app import db
from werkzeug.security import generate_password_hash, check_password_hash


# ================== Event ==================
class Event(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text)
    date = db.Column(db.String(100))
    location = db.Column(db.String(255))
    location_detail = db.Column(db.Text)
    rules = db.Column(db.Text)
    authors = db.Column(db.Text)
    producers = db.Column(db.Text)
    image_url = db.Column(db.String(255))

    ticket_types = db.relationship("TicketType", backref="event", lazy=True)


# ================== TicketType ==================
class TicketType(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50))  # Ví dụ: "Vé thường", "Vé VIP"
    price = db.Column(db.Float)
    stock = db.Column(db.Integer, default=0)
    event_id = db.Column(db.Integer, db.ForeignKey("event.id"), nullable=False)


# ================== User ==================
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)  # Cập nhật thành 255 ký tự

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    bookings = db.relationship("Booking", backref="user", lazy=True)


# ================== Booking ==================
class Booking(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    event_id = db.Column(db.Integer, db.ForeignKey("event.id"), nullable=False)
    ticket_type_id = db.Column(db.Integer, db.ForeignKey("ticket_type.id"), nullable=False)
    quantity = db.Column(db.Integer, nullable=False, default=1)
    selected_seats = db.Column(db.Text)  # JSON string lưu danh sách ghế đã chọn
    total_price = db.Column(db.Float, nullable=False)
    booking_date = db.Column(db.DateTime, nullable=False, default=db.func.current_timestamp())
    status = db.Column(db.String(20), default="confirmed")  # confirmed, cancelled, refunded
    
    # Relationships
    event = db.relationship("Event", backref="bookings")
    ticket_type = db.relationship("TicketType", backref="bookings")

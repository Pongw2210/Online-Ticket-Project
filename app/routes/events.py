from flask import Blueprint, render_template, request, session
from app.data.models import Event,User
from flask_login import current_user

events_bp = Blueprint("events", __name__)

@events_bp.route("/")
def home():
    search = request.args.get("q", "")
    if search:
        events = Event.query.filter(Event.name.ilike(f"%{search}%")).all()
    else:
        events = Event.query.all()

    return render_template("home.html", events=events, search=search, current_user=current_user)

@events_bp.route('/event/<int:event_id>')
def event_detail(event_id):
    event = Event.query.get_or_404(event_id)
    print("[DEBUG] image_url =", event.image_url)
    min_price = None
    if event.ticket_types:
        min_price = min(ticket.price for ticket in event.ticket_types)
    return render_template('event_detail.html', event=event, min_price=min_price)

# @events_bp.route('/new-event')
# def create_event():
#     return render_template('event_organizer/create_event.html')

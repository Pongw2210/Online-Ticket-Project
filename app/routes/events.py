from flask import Blueprint, render_template, request, session, jsonify
from app.models import Event, User, TicketType
from app import db

bp = Blueprint("events", __name__)

@bp.route("/")
def home():
    search = request.args.get("q", "")
    if search:
        events = Event.query.filter(Event.name.ilike(f"%{search}%")).all()
    else:
        events = Event.query.all()

    current_user = None
    if "user_id" in session:
        current_user = User.query.get(session["user_id"])

    return render_template("home.html", events=events, search=search, current_user=current_user)

@bp.route('/event/<int:event_id>')
def event_detail(event_id):
    event = Event.query.get_or_404(event_id)
    print("[DEBUG] image_url =", event.image_url)
    min_price = None
    if event.ticket_types:
        min_price = min(ticket.price for ticket in event.ticket_types)
    return render_template('event_detail.html', event=event, min_price=min_price)

@bp.route('/')
def homepage():
    return render_template('home.html')

@bp.route("/buy-ticket/<int:event_id>")
def buy_ticket(event_id):
    event = Event.query.get_or_404(event_id)
    ticket_types = TicketType.query.filter_by(event_id=event.id).all()
    return render_template("buy_ticket.html", event=event, ticket_types=ticket_types)

@bp.route('/process-order', methods=['POST'])
def process_order():
    data = request.get_json()
    try:
        for item in data['tickets']:
            ticket_id = item['id']
            quantity = int(item['quantity'])
            ticket = TicketType.query.get(ticket_id)
            if ticket and ticket.stock >= quantity:
                ticket.stock -= quantity
            else:
                return jsonify({'success': False, 'message': 'Không đủ vé'}), 400

        db.session.commit()
        return jsonify({'success': True})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 500

@bp.route("/select-seats/<int:event_id>")
def select_seats(event_id):
    event = Event.query.get_or_404(event_id)
    ticket_types = TicketType.query.filter_by(event_id=event.id).all()
    selected_tickets = session.get("selected_tickets", {})  # hoặc test: {"Vé VIP": 2, "Vé Thường": 1}
    return render_template("select_seats.html", event=event, ticket_types=ticket_types, selected_tickets=selected_tickets)



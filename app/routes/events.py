from flask import Blueprint, render_template, request, session, jsonify
from app.data.models import Event, User, TicketType, Booking
from app import db
import json
import qrcode
import io
import base64

events_bp = Blueprint("events", __name__)

@events_bp.route("/")
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

@events_bp.route('/event/<int:event_id>')
def event_detail(event_id):
    event = Event.query.get_or_404(event_id)
    print("[DEBUG] image_url =", event.image_url)
    min_price = None
    if event.ticket_types:
        min_price = min(ticket.price for ticket in event.ticket_types)
    
    # Lấy thông tin user hiện tại nếu đã đăng nhập
    current_user = None
    if "user_id" in session:
        current_user = User.query.get(session["user_id"])
    
    return render_template('event_detail.html', event=event, min_price=min_price, current_user=current_user)

@events_bp.route('/')
def homepage():
    return render_template('home.html')

@events_bp.route("/buy-ticket/<int:event_id>")
def buy_ticket(event_id):
    # Kiểm tra đăng nhập
    if "user_id" not in session:
        return render_template("login_required.html", 
                             message="Vui lòng đăng nhập để mua vé",
                             redirect_url=f"/buy-ticket/{event_id}")
    
    event = Event.query.get_or_404(event_id)
    ticket_types = TicketType.query.filter_by(event_id=event.id).all()
    current_user = User.query.get(session["user_id"])
    
    # Kiểm tra xem có vé nào không
    has_tickets = len(ticket_types) > 0
    
    return render_template("buy_ticket/buy_ticket.html", 
                         event=event, 
                         ticket_types=ticket_types,
                         current_user=current_user,
                         has_tickets=has_tickets)

@events_bp.route('/process-order', methods=['POST'])
def process_order():
    # Kiểm tra đăng nhập
    if "user_id" not in session:
        return jsonify({'success': False, 'message': 'Vui lòng đăng nhập để mua vé'}), 401
    
    data = request.get_json()
    try:
        for item in data['tickets']:
            ticket_id = item['id']
            quantity = int(item['quantity'])
            ticket = TicketType.query.get(ticket_id)
            if ticket and ticket.quantity >= quantity:
                ticket.quantity -= quantity
            else:
                return jsonify({'success': False, 'message': 'Không đủ vé'}), 400

        db.session.commit()
        return jsonify({'success': True})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 500

@events_bp.route("/select-seats/<int:event_id>")
def select_seats(event_id):
    # Kiểm tra đăng nhập
    if "user_id" not in session:
        return render_template("login_required.html", 
                             message="Vui lòng đăng nhập để chọn ghế",
                             redirect_url=f"/select-seats/{event_id}")
    
    event = Event.query.get_or_404(event_id)
    ticket_types = TicketType.query.filter_by(event_id=event.id).all()
    current_user = User.query.get(session["user_id"])

    # Truyền thông tin vé từ database để frontend có thể tạo ghế phù hợp
    return render_template(
        "buy_ticket/select_seats.html",
        event=event,
        ticket_types=ticket_types,
        current_user=current_user
    )

@events_bp.route("/api/ticket-info/<int:event_id>")
def get_ticket_info(event_id):
    """API để lấy thông tin vé từ database"""
    event = Event.query.get_or_404(event_id)
    ticket_types = TicketType.query.filter_by(event_id=event.id).all()
    
    ticket_info = {}
    for ticket in ticket_types:
        ticket_info[ticket.name] = ticket.quantity
    
    return jsonify({
        'success': True,
        'ticket_info': ticket_info,
        'event_name': event.name
    })

@events_bp.route("/api/total-seats/<int:event_id>")
def get_total_seats(event_id):
    """API để lấy tổng số ghế ban đầu từ database"""
    event = Event.query.get_or_404(event_id)
    ticket_types = TicketType.query.filter_by(event_id=event.id).all()
    
    # Tính tổng số ghế ban đầu (không trừ đi số vé đã bán)
    total_seats = {}
    for ticket in ticket_types:
        # Sử dụng quantity ban đầu (tổng số ghế)
        total_seats[ticket.name] = ticket.quantity
    
    return jsonify({
        'success': True,
        'total_seats': total_seats,
        'event_name': event.name
    })

@events_bp.route("/confirm-seats", methods=['POST'])
def confirm_seats():
    """API để xác nhận ghế đã chọn và chuyển đến trang thanh toán"""
    print("🔘 Confirm-seats API called")
    
    # Kiểm tra đăng nhập
    if "user_id" not in session:
        print("❌ User not logged in")
        return jsonify({'success': False, 'message': 'Vui lòng đăng nhập để xác nhận ghế'}), 401
    
    data = request.get_json()
    print(f"📥 Received data: {data}")
    
    selected_seats = data.get('seats', [])
    event_id = data.get('event_id')
    
    print(f"🎫 Selected seats: {selected_seats}")
    print(f"📋 Event ID: {event_id}")
    
    if not selected_seats:
        print("❌ No seats selected")
        return jsonify({'success': False, 'message': 'Chưa chọn ghế nào'}), 400
    
    if not event_id:
        print("❌ No event ID")
        return jsonify({'success': False, 'message': 'Thiếu thông tin sự kiện'}), 400
    
    try:
        user_id = session['user_id']
        print(f"👤 User ID: {user_id}")
        
        # Lấy thông tin vé đã chọn từ localStorage (được gửi từ frontend)
        selected_tickets_data = data.get('selected_tickets', {})
        print(f"🎟️ Selected tickets: {selected_tickets_data}")
        
        # Tính tổng tiền
        total_amount = 0
        for ticket_name, quantity in selected_tickets_data.items():
            if quantity > 0:
                ticket_type = TicketType.query.filter_by(
                    event_id=event_id, 
                    name=ticket_name
                ).first()
                if ticket_type:
                    total_amount += ticket_type.price * quantity
                    print(f"💰 {ticket_name}: {quantity} x {ticket_type.price} = {ticket_type.price * quantity}")
        
        print(f"💰 Total amount: {total_amount}")
        
        # Lưu thông tin vào session để sử dụng ở trang thanh toán
        session['payment_data'] = {
            'event_id': event_id,
            'selected_seats': selected_seats,
            'selected_tickets': selected_tickets_data,
            'total_amount': total_amount
        }
        
        print(f"💾 Payment data saved to session: {session['payment_data']}")
        print(f"✅ User {user_id} đã chọn ghế: {selected_seats}")
        
        response_data = {
            'success': True, 
            'redirect_url': f'/payment/{event_id}',
            'message': f'Đã chọn {len(selected_seats)} ghế. Chuyển đến trang thanh toán.'
        }
        
        print(f"📤 Sending response: {response_data}")
        return jsonify(response_data)
        
    except Exception as e:
        print(f"❌ Lỗi khi xử lý ghế: {str(e)}")
        return jsonify({'success': False, 'message': f'Lỗi khi xử lý thông tin ghế: {str(e)}'}), 500


@events_bp.route("/payment/<int:event_id>")
def payment_page(event_id):
    """Trang thanh toán"""
    print(f"💳 Payment page accessed for event {event_id}")
    
    # Kiểm tra đăng nhập
    if "user_id" not in session:
        print("❌ User not logged in for payment page")
        return render_template("login_required.html", 
                             message="Vui lòng đăng nhập để thanh toán",
                             redirect_url=f"/payment/{event_id}")
    
    # Kiểm tra xem có dữ liệu thanh toán trong session không
    payment_data = session.get('payment_data')
    print(f"💾 Payment data in session: {payment_data}")
    
    if not payment_data or payment_data.get('event_id') != event_id:
        print("❌ No payment data found or event ID mismatch")
        return render_template("login_required.html", 
                             message="Không tìm thấy thông tin đặt vé. Vui lòng thử lại.",
                             redirect_url=f"/")
    
    event = Event.query.get_or_404(event_id)
    current_user = User.query.get(session["user_id"])
    
    print(f"✅ Rendering payment page for event: {event.name}")
    print(f"👤 User: {current_user.username}")
    print(f"🎫 Selected seats: {payment_data['selected_seats']}")
    print(f"💰 Total amount: {payment_data['total_amount']}")
    print(f"📅 Event date: {event.start_datetime} (type: {type(event.start_datetime)})")

    # --- Sinh mã QR chung (giữ nguyên cho các mục khác nếu cần) ---
    qr_data = {
        "amount": payment_data['total_amount'],
        "seats": payment_data['selected_seats']
    }
    qr_str = str(qr_data)
    qr_img = qrcode.make(qr_str)
    buf = io.BytesIO()
    qr_img.save(buf, format='PNG')
    qr_base64 = base64.b64encode(buf.getvalue()).decode('utf-8')
    qr_img_url = f"data:image/png;base64,{qr_base64}"

    # --- Sinh mã QR cho chuyển khoản ngân hàng ---
    bank_info = {
        "bank_name": "Vietcombank",
        "account_number": "1234567890",
        "account_name": "CÔNG TY TNHH ĐẶT VÉ ONLINE",
        "amount": payment_data['total_amount'],
        "content": f"VE_{event.id}_{current_user.id}"
    }
    qr_bank_str = f"BANK:{bank_info['bank_name']}\nSTK:{bank_info['account_number']}\nCHU_TK:{bank_info['account_name']}\nSOTIEN:{bank_info['amount']}\nNOIDUNG:{bank_info['content']}"
    qr_img_bank = qrcode.make(qr_bank_str)
    buf_bank = io.BytesIO()
    qr_img_bank.save(buf_bank, format='PNG')
    qr_base64_bank = base64.b64encode(buf_bank.getvalue()).decode('utf-8')
    qr_img_url_bank = f"data:image/png;base64,{qr_base64_bank}"

    # --- Sinh mã QR cho MOMO ---
    momo_info = {
        "phone": "0909123456",  # Số điện thoại demo
        "amount": payment_data['total_amount'],
        "content": f"VE_{event.id}_{current_user.id}"
    }
    qr_momo_str = f"MOMO:{momo_info['phone']}\nSOTIEN:{momo_info['amount']}\nNOIDUNG:{momo_info['content']}"
    qr_img_momo = qrcode.make(qr_momo_str)
    buf_momo = io.BytesIO()
    qr_img_momo.save(buf_momo, format='PNG')
    qr_base64_momo = base64.b64encode(buf_momo.getvalue()).decode('utf-8')
    qr_img_url_momo = f"data:image/png;base64,{qr_base64_momo}"

    return render_template("buy_ticket/payment.html", 
                         event=event,
                         current_user=current_user,
                         selected_seats=payment_data['selected_seats'],
                         total_amount=payment_data['total_amount'],
                         qr_img_url=qr_img_url,
                         qr_img_url_bank=qr_img_url_bank,
                         qr_img_url_momo=qr_img_url_momo)


@events_bp.route("/process-payment", methods=['POST'])
def process_payment():
    """API để xử lý thanh toán và lưu booking vào database"""
    # Kiểm tra đăng nhập
    if "user_id" not in session:
        return jsonify({'success': False, 'message': 'Vui lòng đăng nhập để thanh toán'}), 401
    
    # Kiểm tra xem có dữ liệu thanh toán trong session không
    payment_data = session.get('payment_data')
    if not payment_data:
        return jsonify({'success': False, 'message': 'Không tìm thấy thông tin đặt vé'}), 400
    
    data = request.get_json()
    payment_method = data.get('payment_method')
    
    if not payment_method:
        return jsonify({'success': False, 'message': 'Vui lòng chọn phương thức thanh toán'}), 400
    
    try:
        user_id = session['user_id']
        event_id = payment_data['event_id']
        selected_seats = payment_data['selected_seats']
        selected_tickets_data = payment_data['selected_tickets']
        
        # Tạo booking cho từng loại vé
        for ticket_name, quantity in selected_tickets_data.items():
            if quantity > 0:
                # Tìm ticket_type trong database
                ticket_type = TicketType.query.filter_by(
                    event_id=event_id, 
                    name=ticket_name
                ).first()
                if ticket_type:
                    # Tính tổng giá tiền
                    total_price = ticket_type.price * quantity

                    # Lọc ghế theo loại vé (xử lý các tên vé tương đương)
                    if ticket_name in ["Vé VIP", "Vé Premium"]:
                        seat_types = ["Vé VIP", "Vé Premium"]
                    elif ticket_name in ["Vé Thường", "Vé Standing"]:
                        seat_types = ["Vé Thường", "Vé Standing"]
                    else:
                        seat_types = [ticket_name]
                    seats_for_ticket = [seat for seat in selected_seats if seat.get('type') in seat_types]
                    
                    # Chuyển đổi seats thành danh sách ID đơn giản
                    seat_ids = [seat.get('id', str(seat)) for seat in seats_for_ticket]

                    # Tạo booking record
                    booking = Booking(
                        user_id=user_id,
                        event_id=event_id,
                        ticket_type_id=ticket_type.id,
                        quantity=quantity,
                        selected_seats=json.dumps(seat_ids),
                        total_price=total_price
                    )
                    db.session.add(booking)
        
        db.session.commit()
        
        # Xóa dữ liệu thanh toán khỏi session
        session.pop('payment_data', None)
        
        print(f"User {user_id} đã thanh toán thành công qua {payment_method}: {selected_seats}")
        
        return jsonify({
            'success': True, 
            'message': f'Thanh toán thành công! Vé đã được gửi đến email của bạn.'
        })
    except Exception as e:
        db.session.rollback()
        print(f"Lỗi khi xử lý thanh toán: {str(e)}")
        return jsonify({'success': False, 'message': f'Lỗi khi xử lý thanh toán: {str(e)}'}), 500


@events_bp.route("/my-tickets")
def my_tickets():
    """Hiển thị vé đã mua của user"""
    # Kiểm tra đăng nhập
    if "user_id" not in session:
        return render_template("login_required.html", 
                             message="Vui lòng đăng nhập để xem vé của bạn",
                             redirect_url="/my-tickets")
    
    user_id = session['user_id']
    user = User.query.get(user_id)
    
    # Lấy tất cả booking của user
    bookings = Booking.query.filter_by(user_id=user_id).order_by(Booking.booking_date.desc()).all()

    # Sinh mã QR cho từng booking
    bookings_with_qr = []
    for booking in bookings:
        # Lấy địa điểm từ EventOffline nếu có,否则 hiển thị "Online Event"
        location = "Online Event"
        if booking.event.event_offline:
            location = booking.event.event_offline.location
        
        qr_info = f"Sự kiện: {booking.event.name}\nLoại vé: {booking.ticket_type.name}\nSố lượng: {booking.quantity}\nĐịa điểm: {location}\nNgày: {booking.event.start_datetime.strftime('%d/%m/%Y %H:%M')}"
        qr_img = qrcode.make(qr_info)
        buf = io.BytesIO()
        qr_img.save(buf, format='PNG')
        qr_base64 = base64.b64encode(buf.getvalue()).decode('utf-8')
        qr_img_url = f"data:image/png;base64,{qr_base64}"
        booking.qr_img_url = qr_img_url
        bookings_with_qr.append(booking)

    return render_template("my_tickets.html", 
                         current_user=user,
                         bookings=bookings_with_qr)

@events_bp.route('/api/booked-seats/<int:event_id>')
def api_booked_seats(event_id):
    """API trả về danh sách tất cả ghế đã được đặt cho event"""
    bookings = Booking.query.filter_by(event_id=event_id).all()
    booked_seats = []
    for booking in bookings:
        if booking.selected_seats:
            try:
                seats = json.loads(booking.selected_seats)
                for seat in seats:
                    if isinstance(seat, dict) and 'id' in seat:
                        booked_seats.append(seat['id'])
                    elif isinstance(seat, str):
                        booked_seats.append(seat)
            except Exception as e:
                continue
    return jsonify({'success': True, 'booked_seats': booked_seats})

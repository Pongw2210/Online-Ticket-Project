from flask_admin import BaseView, expose
from sqlalchemy import func, desc
from flask import request, Response
from datetime import datetime, timedelta
from io import StringIO
import csv

from app.extensions import db
from app.data.models import Event, EventTypeEnum, User, UserEnum, Booking


class StatsView(BaseView):
    @expose('/')
    def index(self):
        # ----- Params -----
        start_str = request.args.get('start')
        end_str = request.args.get('end')
        current_tab = request.args.get('tab', 'event')
        export = request.args.get('export')

        # Default: last 30 days
        if start_str and end_str:
            try:
                start_date = datetime.strptime(start_str, '%Y-%m-%d')
                end_date = datetime.strptime(end_str, '%Y-%m-%d') + timedelta(days=1)
            except Exception:
                start_date = datetime.today() - timedelta(days=30)
                end_date = datetime.today() + timedelta(days=1)
        else:
            start_date = datetime.today() - timedelta(days=30)
            end_date = datetime.today() + timedelta(days=1)

        # Previous period
        delta = end_date - start_date
        prev_start = start_date - delta
        prev_end = start_date

        # ----- Event by type -----
        q_event_type = db.session.query(
            Event.event_type, func.count(Event.id)
        ).group_by(Event.event_type).all()
        event_counts = {et: cnt for et, cnt in q_event_type}
        event_labels = [e.value for e in EventTypeEnum]
        event_data = [event_counts.get(e, 0) for e in EventTypeEnum]
        event_table = list(zip(event_labels, event_data))

        # ----- User by role -----
        q_user_role = db.session.query(
            User.role, func.count(User.id)
        ).group_by(User.role).all()
        user_counts = {r: cnt for r, cnt in q_user_role}
        user_labels = [r.value for r in UserEnum]
        user_data = [user_counts.get(r, 0) for r in UserEnum]
        user_table = list(zip(user_labels, user_data))

        # ----- Bookings by date -----
        booking_pairs = db.session.query(
            func.date(Booking.booking_date).label("date"),
            func.count(Booking.id)
        ).filter(
            Booking.booking_date >= start_date,
            Booking.booking_date < end_date
        ).group_by(func.date(Booking.booking_date)) \
         .order_by(func.date(Booking.booking_date)).all()

        booking_labels = [str(d) for d, _ in booking_pairs]
        booking_data = [c for _, c in booking_pairs]
        booking_table = list(zip(booking_labels, booking_data))

        # ----- Summary cards -----
        total_events = db.session.query(func.count(Event.id)).scalar() or 0
        total_users = db.session.query(func.count(User.id)).scalar() or 0
        total_bookings = db.session.query(func.count(Booking.id)).filter(
            Booking.booking_date >= start_date, Booking.booking_date < end_date
        ).scalar() or 0

        total_revenue = db.session.query(
            func.coalesce(func.sum(Booking.final_price), 0)
        ).filter(
            Booking.booking_date >= start_date,
            Booking.booking_date < end_date
        ).scalar() or 0.0

        prev_bookings = db.session.query(func.count(Booking.id)).filter(
            Booking.booking_date >= prev_start, Booking.booking_date < prev_end
        ).scalar() or 0

        def pct_change(current, previous):
            if previous == 0:
                return None if current == 0 else 100.0
            return round(((current - previous) / previous) * 100.0, 1)

        bookings_pct = pct_change(total_bookings, prev_bookings)

        # ----- Top 5 events -----
        q_top_events = db.session.query(
            Event.id, Event.name, func.count(Booking.id).label('cnt')
        ).join(Booking, Booking.event_id == Event.id) \
         .filter(
            Booking.booking_date >= start_date,
            Booking.booking_date < end_date
         ).group_by(Event.id, Event.name) \
         .order_by(desc('cnt')).limit(5).all()

        top_events = [{'event_id': eid, 'title': name, 'count': cnt} for eid, name, cnt in q_top_events]

        # ----- Top 5 users -----
        q_top_users = db.session.query(
            User.id, User.username, func.count(Booking.id).label('cnt')
        ).join(Booking, Booking.user_id == User.id) \
         .filter(
            Booking.booking_date >= start_date,
            Booking.booking_date < end_date
         ).group_by(User.id, User.username) \
         .order_by(desc('cnt')).limit(5).all()

        top_users = [{'user_id': uid, 'name': uname, 'count': cnt} for uid, uname, cnt in q_top_users]

        # ----- CSV Export -----
        if export == 'csv':
            si = StringIO()
            writer = csv.writer(si)

            writer.writerow(['Summary'])
            writer.writerow(['Metric', 'Value'])
            writer.writerow(['Total events', total_events])
            writer.writerow(['Total users', total_users])
            writer.writerow(['Total bookings', total_bookings])
            writer.writerow(['Total revenue', total_revenue])
            writer.writerow([])

            writer.writerow(['Bookings by date'])
            writer.writerow(['Date', 'Count'])
            for label, cnt in booking_table:
                writer.writerow([label, cnt])

            writer.writerow([])
            writer.writerow(['Top 5 events'])
            writer.writerow(['Event ID', 'Name', 'Count'])
            for e in top_events:
                writer.writerow([e['event_id'], e['title'], e['count']])

            writer.writerow([])
            writer.writerow(['Top 5 users'])
            writer.writerow(['User ID', 'Name', 'Count'])
            for u in top_users:
                writer.writerow([u['user_id'], u['name'], u['count']])

            output = si.getvalue()
            si.close()
            filename = f"stats_{start_date.date()}_{(end_date - timedelta(days=1)).date()}.csv"
            return Response(output, mimetype="text/csv",
                            headers={"Content-disposition": f"attachment; filename={filename}"})

        # ----- Render -----
        return self.render(
            'admin/stats.html',
            event_labels=event_labels, event_data=event_data, event_table=event_table,
            user_labels=user_labels, user_data=user_data, user_table=user_table,
            booking_labels=booking_labels, booking_data=booking_data, booking_table=booking_table,
            start_date=start_date.strftime('%Y-%m-%d'),
            end_date=(end_date - timedelta(days=1)).strftime('%Y-%m-%d'),
            current_tab=current_tab,
            total_events=total_events, total_users=total_users,
            total_bookings=total_bookings, total_revenue=total_revenue,
            bookings_pct=bookings_pct,
            top_events=top_events, top_users=top_users
        )

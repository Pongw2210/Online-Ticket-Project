from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView

from flask_admin.menu import MenuLink
from flask_admin import AdminIndexView, expose
from sqlalchemy import func
from flask import url_for
from app.data.models import Event, EventTypeEnum
from app.extensions import db
from app.admin_stats import StatsView



flask_admin = Admin(name="Ticket Admin", template_mode="bootstrap4")


# AdminIndexView có inject CSS
class MyAdminIndexView(AdminIndexView):

    @expose('/')
    def index(self):
        from app.data.models import (
            User, Event, Customer, EventOrganizer, EventOnline, EventOffline,
            Booking, EventTypeEnum, UserEnum
        )

        # Thống kê tổng số bản ghi từng bảng
        counts_summary = {
            "User": db.session.query(func.count(User.id)).scalar(),
            "Customer": db.session.query(func.count(Customer.id)).scalar(),
            "Event Organizer": db.session.query(func.count(EventOrganizer.id)).scalar(),
            "Event Online": db.session.query(func.count(EventOnline.id)).scalar(),
            "Event Offline": db.session.query(func.count(EventOffline.id)).scalar(),
            "Booking": db.session.query(func.count(Booking.id)).scalar(),
        }

        # Biểu đồ Event theo loại
        q_event_type = db.session.query(Event.event_type, func.count(Event.id)).group_by(Event.event_type).all()
        event_counts = {item[0]: item[1] for item in q_event_type}
        event_labels = [e.value for e in EventTypeEnum]
        event_data = [event_counts.get(e, 0) for e in EventTypeEnum]

        # Biểu đồ User theo vai trò
        q_user_role = db.session.query(User.role, func.count(User.id)).group_by(User.role).all()
        user_counts = {item[0]: item[1] for item in q_user_role}
        user_labels = [r.value for r in UserEnum]
        user_data = [user_counts.get(r, 0) for r in UserEnum]

        return self.render(
            'admin/index.html',
            counts_summary=counts_summary,
            event_labels=event_labels,
            event_data=event_data,
            user_labels=user_labels,
            user_data=user_data
        )


# ModelView cũng inject CSS
class MyModelView(ModelView):
    def render(self, template, **kwargs):
        extras = self._template_args.get('extra_css', [])
        extras.append(url_for('static', filename='css/custom.css'))
        self._template_args['extra_css'] = extras
        return super().render(template, **kwargs)


flask_admin = Admin(
    name="Ticket Admin",
    template_mode="bootstrap4",
    index_view=MyAdminIndexView()
)



def init_admin(app):
    from app.data.models import User, Event, Customer, EventOrganizer, EventOnline, EventOffline, Booking
    flask_admin.add_view(MyModelView(User, db.session, endpoint="admin_user"))
    flask_admin.add_view(MyModelView(Event, db.session))
    flask_admin.add_view(MyModelView(Customer, db.session))
    flask_admin.add_view(MyModelView(EventOrganizer, db.session))
    flask_admin.add_view(MyModelView(EventOnline, db.session))
    flask_admin.add_view(MyModelView(EventOffline, db.session))
    flask_admin.add_view(MyModelView(Booking, db.session))
    flask_admin.add_view(StatsView(name="Thống kê", endpoint="stats"))
    flask_admin.add_link(MenuLink(name="Duyệt sự kiện", url="/admin/approve-events"))
    flask_admin.add_link(MenuLink(name="Đăng xuất", url="/logout"))
    flask_admin.init_app(app)
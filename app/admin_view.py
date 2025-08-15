from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView
from flask_admin.menu import MenuLink

flask_admin = Admin(name="Ticket Admin", template_mode="bootstrap4")


flask_admin.add_link(MenuLink(name="Duyệt sự kiện", url="/admin/approve-events"))
flask_admin.add_link(MenuLink(name="Đăng xuất", url="/logout"))


def init_admin(app):
    from app import db
    from app.data.models import User,Event,Customer,EventOrganizer,EventOnline,EventOffline

    # Dùng ModelView mặc định, không tùy biến
    flask_admin.add_view(ModelView(User, db.session))
    flask_admin.add_view(ModelView(Event, db.session))
    flask_admin.add_view(ModelView(Customer, db.session))
    flask_admin.add_view(ModelView(EventOrganizer, db.session))
    flask_admin.add_view(ModelView(EventOnline, db.session))
    flask_admin.add_view(ModelView(EventOffline, db.session))

    flask_admin.init_app(app)
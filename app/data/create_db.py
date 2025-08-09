import hashlib
from datetime import datetime
from sqlalchemy import inspect
from app import create_app, db
from app.data.models import Admin, User, Customer, UserEnum, EventOrganizer, TicketType, Event, EventOnline, \
    EventOffline, EventTypeEnum, EventFormatEnum

app = create_app()

def seed_admin_user():
    admin1 = Admin(fullname="Đặng Mỹ Ngọc", email="dmn@gmail.com", gender="Nữ")
    db.session.add(admin1)
    uAdmin1 = User(username="userAdmin", email="useradmin@gmail.com", password=str(hashlib.md5("123".encode('utf-8')).hexdigest()),
                   avatar="https://res.cloudinary.com/dgqx9xde1/image/upload/v1744900055/User2_qjswcy.webp",
                   role=UserEnum.ADMIN)
    uAdmin1.admin = admin1
    db.session.add(uAdmin1)
    db.session.commit()

def seed_customer_user():
    cus1 = Customer(fullname="Nguyễn Ngọc Anh", email="nna@gmail.com", gender="Nữ", dob=datetime(2000, 1, 1),
                    number_phone="0987654321")
    db.session.add(cus1)
    ucus1 = User(username="userKhachHang", email="userkhachhang@gmail.com", password=str(hashlib.md5("123".encode('utf-8')).hexdigest()),
                 avatar="https://res.cloudinary.com/dgqx9xde1/image/upload/v1744900183/User3_byutxj.jpg",
                 role=UserEnum.KHACH_HANG)
    ucus1.customer = cus1
    db.session.add(ucus1)
    db.session.commit()

def seed_event_organizer_user():
    event_organizer1 = EventOrganizer(fullname="Trần Bảo Ngọc", email="tbn@gmail.com", gender="Nữ")
    db.session.add(event_organizer1)
    uEvent_organizer1 = User(username="userNguoiToChuc", email="usertochnuc@gmail.com",
                             password=str(hashlib.md5("123".encode('utf-8')).hexdigest()),
                             role=UserEnum.NGUOI_TO_CHUC)
    uEvent_organizer1.event_organizer = event_organizer1
    db.session.add(uEvent_organizer1)
    db.session.commit()

def seed_event_offline():
    offline_events_data = [
        {
            "name": "Gốm Show - Hà Nội",
            "description": "Gốm Show là dự án nghệ thuật âm nhạc sáng tạo...",
            "start_datetime": datetime(2025, 7, 31, 19, 30),
            "end_datetime": datetime(2025, 7, 31, 21, 30),
            "venue_name": "Nhà hát Lớn Hà Nội",
            "location": "1 Tràng Tiền, Phan Chu Trinh, Hoàn Kiếm, Hà Nội",
            "rules": "Không mang vũ khí, chất cấm, không quay phim...",
            "authors": "Đạo diễn Nguyễn Văn A, Biên đạo Trần Văn B",
            "producers": "SKY SOUND PRODUCTION, Nhà hát Lớn Hà Nội",
            "image_url": "https://res.cloudinary.com/dgqx9xde1/image/upload/v1753612716/gomshow_spfsbk.jpg"
        },
        {
            "name": "Hòa Nhạc Mùa Thu",
            "description": "Chương trình âm nhạc cổ điển được trình diễn bởi dàn nhạc giao hưởng quốc gia...",
            "start_datetime": datetime(2025, 9, 5, 19, 0),
            "end_datetime": datetime(2025, 9, 5, 21, 0),
            "venue_name": "Nhà hát Lớn TP.HCM",
            "location": "7 Công Trường Lam Sơn, Bến Nghé, Quận 1, TP.HCM",
            "rules": "Trang phục lịch sự. Không mang đồ ăn, nước uống...",
            "authors": "NSƯT Lê Hồng Sơn",
            "producers": "Dàn nhạc giao hưởng Quốc gia",
            "image_url": "https://res.cloudinary.com/dgqx9xde1/image/upload/v1753612717/hoa-nhac-mua-thu_r3vwtt.jpg"
        },
        {
            "name": "Live Concert Sơn Tùng M-TP",
            "description": "Đêm nhạc 'Sky Tour' là sự kiện âm nhạc đỉnh cao của Sơn Tùng M-TP...",
            "start_datetime": datetime(2025, 8, 12, 20, 0),
            "end_datetime": datetime(2025, 8, 12, 22, 30),
            "venue_name": "Sân vận động Mỹ Đình",
            "location": "Lê Đức Thọ, Nam Từ Liêm, Hà Nội",
            "rules": "Không mang đồ ăn, nước uống. Vé không dành cho trẻ dưới 8 tuổi...",
            "authors": "Sơn Tùng M-TP",
            "producers": "M-TP Entertainment",
            "image_url": "https://res.cloudinary.com/dgqx9xde1/image/upload/v1753612717/mtp-live_aelu1w.jpg"
        },
        {
            "name": "Đêm Nhạc Trịnh – Gọi Tên Bốn Mùa",
            "description": "Một đêm nhạc lắng đọng với các bản tình ca bất hủ của nhạc sĩ Trịnh Công Sơn...",
            "start_datetime": datetime(2025, 8, 25, 20, 0),
            "end_datetime": datetime(2025, 8, 25, 22, 0),
            "venue_name": "Nhà hát Hòa Bình",
            "location": "240 Đường 3/2, Quận 10, TP.HCM",
            "rules": "Trang phục lịch sự. Không quay phim...",
            "authors": "Hồng Nhung, Đức Tuấn",
            "producers": "Công ty Truyền Thông Mưa",
            "image_url": "https://res.cloudinary.com/dgqx9xde1/image/upload/v1753612716/demnhactrinh_wdtcul.jpg"
        },
        {
            "name": "Sân Khấu Hài – Tám Chuyện Cuối Tuần",
            "description": "Một buổi biểu diễn hài kịch vui nhộn với các nghệ sĩ nổi tiếng...",
            "start_datetime": datetime(2025, 8, 17, 19, 30),
            "end_datetime": datetime(2025, 8, 17, 21, 30),
            "venue_name": "Nhà hát Kịch Sài Gòn",
            "location": "30 Trần Hưng Đạo, Quận 1, TP.HCM",
            "rules": "Không hoàn vé. Không mang đồ ăn, quay phim...",
            "authors": "Nhóm Hài Thứ Bảy, MC Đại Nghĩa",
            "producers": "Công ty Giải Trí Cười Vui",
            "image_url": "https://res.cloudinary.com/dgqx9xde1/image/upload/v1753612716/haicuoi_crzki5.jpg"
        },
        {
            "name": "Gala Hài Kịch 2025",
            "description": "Sự kiện quy tụ Trấn Thành, Việt Hương, Trường Giang... tiểu phẩm đặc sắc và thông điệp nhân văn.",
            "start_datetime": datetime(2025, 11, 25, 18, 30),
            "end_datetime": datetime(2025, 11, 25, 21, 30),
            "venue_name": "Nhà hát Bến Thành",
            "location": "6 Mạc Đĩnh Chi, Quận 1, TP.HCM",
            "rules": "Không trẻ em dưới 8 tuổi. Không quay phim...",
            "authors": "Trấn Thành, Việt Hương",
            "producers": "Hài TV & Showbiz Việt",
            "image_url": "https://res.cloudinary.com/dgqx9xde1/image/upload/v1753612716/gala-hai_l9vlnz.jpg"
        },
        {
            "name": "Kịch Trinh Thám: 'Lưới Trời'",
            "description": "Vở kịch trinh thám đầy kịch tính và ánh sáng đỉnh cao...",
            "start_datetime": datetime(2025, 10, 30, 19, 0),
            "end_datetime": datetime(2025, 10, 30, 21, 0),
            "venue_name": "Sân khấu kịch Idecaf",
            "location": "28 Lê Thánh Tôn, Quận 1, TP.HCM",
            "rules": "Không trẻ dưới 8 tuổi. Vé hết hiệu lực sau 15 phút...",
            "authors": "Đạo diễn Nguyễn Ngọc Bảo",
            "producers": "Nhà hát kịch Idecaf",
            "image_url": "https://res.cloudinary.com/dgqx9xde1/image/upload/v1753612717/kich-luoi-troi_nwzh6p.jpg"
        },
        {
            "name": "Rap Việt All Stars",
            "description": "Sự kiện âm nhạc hoành tráng quy tụ những rapper nổi bật như Binz, Karik...",
            "start_datetime": datetime(2025, 12, 10, 19, 30),
            "end_datetime": datetime(2025, 12, 10, 23, 0),
            "venue_name": "Sân vận động Thống Nhất",
            "location": "30 Nguyễn Kim, Quận 10, TP.HCM",
            "rules": "Không trẻ em dưới 8 tuổi. Vé hết hiệu lực sau 15 phút...",
            "authors": "Binz, Wowy, Rhymastic",
            "producers": "VieON, Rap Việt Production",
            "image_url": "https://res.cloudinary.com/dgqx9xde1/image/upload/v1753612717/rapviet_pxr0ye.jpg"
        },
        {
            "name": "Triển Lãm Tranh 3D Quốc Tế",
            "description": "Một thế giới nghệ thuật sống động qua tranh 3D ấn tượng...",
            "start_datetime": datetime(2025, 10, 1, 8, 0),
            "end_datetime": datetime(2025, 10, 5, 18, 0),
            "venue_name": "Trung tâm triển lãm SECC",
            "location": "799 Nguyễn Văn Linh, Quận 7, TP.HCM",
            "rules": "Không trẻ em dưới 8 tuổi. Không quay phim...",
            "authors": "Tổ chức nghệ thuật 3D Asia",
            "producers": "SECC phối hợp Bộ Văn hóa",
            "image_url": "https://res.cloudinary.com/dgqx9xde1/image/upload/v1753612717/trienlam3d_gsqm4t.jpg"
        },
        {
            "name": "Thơ - Nhạc Trịnh Công Sơn",
            "description": "Đêm nhạc tưởng nhớ Trịnh Công Sơn với không gian nhẹ nhàng...",
            "start_datetime": datetime(2025, 4, 1, 19, 0),
            "end_datetime": datetime(2025, 4, 1, 21, 0),
            "venue_name": "Nhà hát Hòa Bình",
            "location": "240 Đường 3 Tháng 2, Quận 10, TP.HCM",
            "rules": "Không trẻ em dưới 8 tuổi. Vé hết hiệu lực sau 15 phút...",
            "authors": "Hồng Nhung, Đức Tuấn",
            "producers": "Gia đình Trịnh Công Sơn & Nhà hát Hòa Bình",
            "image_url": "https://res.cloudinary.com/dgqx9xde1/image/upload/v1753612718/trinhcongson_pu5pmv.jpg"
        },
        {
            "name": "Hội Thảo Công Nghệ AI 2025",
            "description": "Hội thảo AI quy tụ chuyên gia trong nước và quốc tế...",
            "start_datetime": datetime(2025, 9, 15, 9, 0),
            "end_datetime": datetime(2025, 9, 15, 17, 0),
            "venue_name": "Trung tâm Hội nghị Quốc gia",
            "location": "Cổng số 1 Đại lộ Thăng Long, Nam Từ Liêm, Hà Nội",
            "rules": "Không trẻ em dưới 8 tuổi. Vé hết hiệu lực sau 15 phút...",
            "authors": "TS. Nguyễn Văn A, Prof. John Doe",
            "producers": "Bộ KH&CN & TechTalks Vietnam",
            "image_url": "https://res.cloudinary.com/dgqx9xde1/image/upload/v1753612715/ai-conference_kvlkfl.jpg"
        },
        {
            "name": "Đêm Nhạc Acoustic 'Góc Phố Xưa'",
            "description": "Sự kiện âm nhạc dành cho những tâm hồn yêu sự bình yên, hoài niệm...",
            "start_datetime": datetime(2025, 8, 20, 20, 0),
            "end_datetime": datetime(2025, 8, 20, 22, 0),
            "venue_name": "Trixie Cafe & Lounge",
            "location": "165 Thái Hà, Đống Đa, Hà Nội",
            "rules": "Không trẻ em dưới 8 tuổi. Vé hết hiệu lực sau 15 phút...",
            "authors": "Minh Vương M4U, Trang",
            "producers": "Trixie Music Group",
            "image_url": "https://res.cloudinary.com/dgqx9xde1/image/upload/v1753612715/acoustic_akxfdk.jpg"
        }
    ]

    organizer = EventOrganizer.query.filter_by(fullname="Trần Bảo Ngọc").first()

    for data in offline_events_data:
        event = Event(
            name=data["name"],
            description=data["description"],
            start_datetime=data["start_datetime"],
            end_datetime=data["end_datetime"],
            rules=data["rules"],
            authors=data["authors"],
            producers=data["producers"],
            image_url=data["image_url"],
            event_format = EventFormatEnum.OFFLINE,
            event_type = EventTypeEnum.NGHE_THUAT,
            organizer_id = organizer.id
        )
        db.session.add(event)
        db.session.flush()  # để có event.id

        offline = EventOffline(
            event_id=event.id,
            venue_name=data["venue_name"],
            location=data["location"]
        )
        db.session.add(offline)

    db.session.commit()

def seed_ticket_type():
    ticket_types = [
        TicketType(name='Vé Thường', price=250000, quantity=50 , event_id=1),
        TicketType(name='Vé VIP', price=500000, quantity=50,  event_id=1),
        TicketType(name='Vé Standing', price=300000, quantity=50, event_id=2),
        TicketType(name='Vé VIP', price=650000, quantity=50, event_id=2),
        TicketType(name='Vé Thường', price=200000, quantity=50, event_id=3),
        TicketType(name='Vé Premium', price=400000,quantity=50, event_id=3),
    ]

    db.session.add_all(ticket_types)
    db.session.commit()

if __name__ == "__main__":
    with app.app_context():
        db.drop_all()
        db.create_all()

        seed_customer_user()
        seed_admin_user()
        seed_event_organizer_user()

        seed_event_offline()
        seed_ticket_type()
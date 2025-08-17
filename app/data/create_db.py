# create_db.py
import hashlib
from datetime import datetime

from app import create_app
from app.extensions import db
from app.data.models import (
    Admin, User, Customer, UserEnum, EventOrganizer, TicketType, Event, EventOnline,
    EventOffline, EventTypeEnum, EventFormatEnum, StatusEventEnum
)

app = create_app()

def seed_admin_user():
    admin1 = Admin(fullname="Đặng Mỹ Ngọc", email="dmn@gmail.com", gender="Nữ")
    db.session.add(admin1)
    uAdmin1 = User(
        username="userAdmin",
        email="useradmin@gmail.com",
        password=str(hashlib.md5("123".encode('utf-8')).hexdigest()),
        avatar="https://res.cloudinary.com/dgqx9xde1/image/upload/v1744900055/User2_qjswcy.webp",
        role=UserEnum.ADMIN
    )
    uAdmin1.admin = admin1
    db.session.add(uAdmin1)
    db.session.commit()

def seed_customer_user():
    cus1 = Customer(
        fullname="Nguyễn Ngọc Anh",
        email="2254052006bong@ou.edu.vn",
        gender="Nữ",
        dob=datetime(2000, 1, 1),
        number_phone="0987654321"
    )
    db.session.add(cus1)
    ucus1 = User(
        username="userKhachHang",
        email="2254052006bong@ou.edu.vn",
        password=str(hashlib.md5("123".encode('utf-8')).hexdigest()),
        avatar="https://res.cloudinary.com/dgqx9xde1/image/upload/v1744900183/User3_byutxj.jpg",
        role=UserEnum.KHACH_HANG
    )
    ucus1.customer = cus1
    db.session.add(ucus1)
    db.session.commit()

def seed_event_organizer_user():
    event_organizer1 = EventOrganizer(fullname="Trần Bảo Ngọc", email="tbn@gmail.com", gender="Nữ")
    db.session.add(event_organizer1)
    uEvent_organizer1 = User(
        username="userNguoiToChuc",
        email="usertochnuc@gmail.com",
        password=str(hashlib.md5("123".encode('utf-8')).hexdigest()),
        role=UserEnum.NGUOI_TO_CHUC
    )
    uEvent_organizer1.event_organizer = event_organizer1
    db.session.add(uEvent_organizer1)

    event_organizer2 = EventOrganizer(fullname="Test", email="tbn@gmail.com", gender="Nữ")
    db.session.add(event_organizer2)
    uEvent_organizer2 = User(
        username="userNguoiToChuc1",
        email="usertochnuc1@gmail.com",
        password=str(hashlib.md5("123".encode('utf-8')).hexdigest()),
        role=UserEnum.NGUOI_TO_CHUC
    )
    uEvent_organizer2.event_organizer = event_organizer2
    db.session.add(uEvent_organizer2)
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
            "image_url": "https://res.cloudinary.com/dgqx9xde1/image/upload/v1753612716/gomshow_spfsbk.jpg",
            "has_seat": False
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
            "image_url": "https://res.cloudinary.com/dgqx9xde1/image/upload/v1753612717/hoa-nhac-mua-thu_r3vwtt.jpg",
            "has_seat": False
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
            "image_url": "https://res.cloudinary.com/dgqx9xde1/image/upload/v1753612717/mtp-live_aelu1w.jpg",
            "has_seat": True
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
            "image_url": "https://res.cloudinary.com/dgqx9xde1/image/upload/v1753612716/demnhactrinh_wdtcul.jpg",
            "has_seat": False
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
            "image_url": "https://res.cloudinary.com/dgqx9xde1/image/upload/v1753612716/haicuoi_crzki5.jpg",
            "has_seat": False
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
            "image_url": "https://res.cloudinary.com/dgqx9xde1/image/upload/v1753612716/gala-hai_l9vlnz.jpg",
            "has_seat": False
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
            "image_url": "https://res.cloudinary.com/dgqx9xde1/image/upload/v1753612717/kich-luoi-troi_nwzh6p.jpg",
            "has_seat": False
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
            "image_url": "https://res.cloudinary.com/dgqx9xde1/image/upload/v1753612717/rapviet_pxr0ye.jpg",
            "has_seat": False
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
            "image_url": "https://res.cloudinary.com/dgqx9xde1/image/upload/v1753612717/trienlam3d_gsqm4t.jpg",
            "has_seat": False
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
            "image_url": "https://res.cloudinary.com/dgqx9xde1/image/upload/v1753612718/trinhcongson_pu5pmv.jpg",
            "has_seat": False
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
            "image_url": "https://res.cloudinary.com/dgqx9xde1/image/upload/v1753612715/ai-conference_kvlkfl.jpg",
            "has_seat": False
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
            "image_url": "https://res.cloudinary.com/dgqx9xde1/image/upload/v1753612715/acoustic_akxfdk.jpg",
            "has_seat": False
        },
        # ================= NHẠC SỐNG =================
        {
            "name": "Rock Việt Festival",
            "description": "Lễ hội Rock lớn nhất năm với các ban nhạc nổi tiếng.",
            "start_datetime": datetime(2025, 9, 1, 19, 0),
            "end_datetime": datetime(2025, 9, 1, 22, 0),
            "venue_name": "SVĐ Mỹ Đình",
            "location": "Lê Đức Thọ, Nam Từ Liêm, Hà Nội",
            "rules": "Không mang đồ ăn, nước uống.",
            "authors": "Ban nhạc Bức Tường",
            "producers": "Music Media",
            "image_url": "https://res.cloudinary.com/dgqx9xde1/image/upload/v1753612716/rockviet.jpg",
            "has_seat": True,
            "event_type": EventTypeEnum.NHAC_SONG

        },
        {
            "name": "Acoustic Night",
            "description": "Đêm nhạc Acoustic lãng mạn và nhẹ nhàng.",
            "start_datetime": datetime(2025, 9, 2, 20, 0),
            "end_datetime": datetime(2025, 9, 2, 22, 0),
            "venue_name": "Nhà hát Lớn Hà Nội",
            "location": "1 Tràng Tiền, Hoàn Kiếm, Hà Nội",
            "rules": "Không hút thuốc trong khán phòng.",
            "authors": "Nhiều ca sĩ Acoustic",
            "producers": "Acoustic Group",
            "image_url": "https://res.cloudinary.com/dgqx9xde1/image/upload/v1753612716/acoustic.jpg",
            "has_seat": False,
            "event_type": EventTypeEnum.NHAC_SONG
        },
        {
            "name": "EDM Night Party",
            "description": "Đêm hội EDM cùng các DJ hàng đầu thế giới.",
            "start_datetime": datetime(2025, 9, 5, 21, 0),
            "end_datetime": datetime(2025, 9, 6, 2, 0),
            "venue_name": "Sân vận động Quân khu 7",
            "location": "202 Hoàng Văn Thụ, Tân Bình, TP.HCM",
            "rules": "Không sử dụng chất kích thích.",
            "authors": "DJ Wang, DJ Dero",
            "producers": "MusicHub",
            "image_url": "https://res.cloudinary.com/dgqx9xde1/image/upload/v1753612716/edm.jpg",
            "has_seat": False,
            "event_type": EventTypeEnum.NHAC_SONG
        },
        {
            "name": "Live Concert Mỹ Tâm",
            "description": "Đêm nhạc đặc biệt của ca sĩ Mỹ Tâm.",
            "start_datetime": datetime(2025, 9, 10, 20, 0),
            "end_datetime": datetime(2025, 9, 10, 23, 0),
            "venue_name": "Nhà hát Hòa Bình",
            "location": "240 Đường 3/2, Quận 10, TP.HCM",
            "rules": "Không mang máy quay chuyên nghiệp.",
            "authors": "Mỹ Tâm",
            "producers": "MT Entertainment",
            "image_url": "https://res.cloudinary.com/dgqx9xde1/image/upload/v1753612716/mytam.jpg",
            "has_seat": True,
            "event_type": EventTypeEnum.NHAC_SONG
        },
        {
            "name": "Indie Music Night",
            "description": "Sân chơi dành cho các ban nhạc indie Việt.",
            "start_datetime": datetime(2025, 9, 12, 19, 30),
            "end_datetime": datetime(2025, 9, 12, 22, 30),
            "venue_name": "Hard Rock Cafe",
            "location": "39 Lê Duẩn, Quận 1, TP.HCM",
            "rules": "Mua đồ uống kèm vé vào cửa.",
            "authors": "Nhiều ban nhạc indie",
            "producers": "IndieVN",
            "image_url": "https://res.cloudinary.com/dgqx9xde1/image/upload/v1753612716/indie.jpg",
            "has_seat": False,
            "event_type": EventTypeEnum.NHAC_SONG
        },
        {
            "name": "Rap Việt Show",
            "description": "Sự kiện quy tụ các rapper nổi bật của Rap Việt.",
            "start_datetime": datetime(2025, 9, 15, 19, 0),
            "end_datetime": datetime(2025, 9, 15, 23, 0),
            "venue_name": "Sân vận động Thống Nhất",
            "location": "30 Nguyễn Kim, Quận 10, TP.HCM",
            "rules": "Không trẻ em dưới 8 tuổi.",
            "authors": "Binz, Karik, Rhymastic",
            "producers": "VieON",
            "image_url": "https://res.cloudinary.com/dgqx9xde1/image/upload/v1753612716/rapviet.jpg",
            "has_seat": True,
            "event_type": EventTypeEnum.NHAC_SONG
        },
        {
            "name": "Jazz Night",
            "description": "Không gian âm nhạc Jazz sang trọng.",
            "start_datetime": datetime(2025, 9, 18, 20, 0),
            "end_datetime": datetime(2025, 9, 18, 22, 0),
            "venue_name": "Saigon Opera House",
            "location": "7 Công Trường Lam Sơn, Quận 1, TP.HCM",
            "rules": "Trang phục lịch sự.",
            "authors": "Ban nhạc Jazz Việt",
            "producers": "Saigon Orchestra",
            "image_url": "https://res.cloudinary.com/dgqx9xde1/image/upload/v1753612716/jazz.jpg",
            "has_seat": True,
            "event_type": EventTypeEnum.NHAC_SONG
        },
        {
            "name": "Kpop Cover Night",
            "description": "Sự kiện dành cho fan Kpop với nhiều nhóm nhảy cover.",
            "start_datetime": datetime(2025, 9, 20, 18, 0),
            "end_datetime": datetime(2025, 9, 20, 21, 0),
            "venue_name": "SVĐ Quân khu 5",
            "location": "Nguyễn Văn Linh, Đà Nẵng",
            "rules": "Không sử dụng pháo sáng.",
            "authors": "Các nhóm dance cover",
            "producers": "Kpop Fans VN",
            "image_url": "https://res.cloudinary.com/dgqx9xde1/image/upload/v1753612716/kpop.jpg",
            "has_seat": False,
            "event_type": EventTypeEnum.NHAC_SONG
        },
        {
            "name": "Bolero Night",
            "description": "Đêm nhạc Bolero dành cho khán giả trung niên.",
            "start_datetime": datetime(2025, 9, 22, 19, 30),
            "end_datetime": datetime(2025, 9, 22, 22, 0),
            "venue_name": "Nhà hát Bến Thành",
            "location": "6 Mạc Đĩnh Chi, Quận 1, TP.HCM",
            "rules": "Trang phục chỉnh tề.",
            "authors": "Danh ca Như Quỳnh",
            "producers": "Bolero Media",
            "image_url": "https://res.cloudinary.com/dgqx9xde1/image/upload/v1753612716/bolero.jpg",
            "has_seat": True,
            "event_type": EventTypeEnum.NHAC_SONG
        },
        {
            "name": "Symphony Gala",
            "description": "Đêm nhạc giao hưởng đặc biệt với dàn nhạc quốc tế.",
            "start_datetime": datetime(2025, 9, 25, 19, 0),
            "end_datetime": datetime(2025, 9, 25, 22, 0),
            "venue_name": "Nhà hát Lớn Hà Nội",
            "location": "1 Tràng Tiền, Hoàn Kiếm, Hà Nội",
            "rules": "Không quay phim, chụp ảnh.",
            "authors": "Dàn nhạc giao hưởng Việt - Mỹ",
            "producers": "Opera House",
            "image_url": "https://res.cloudinary.com/dgqx9xde1/image/upload/v1753612716/symphony.jpg",
            "has_seat": True,
            "event_type": EventTypeEnum.NHAC_SONG
        },

        # ================= THỂ THAO =================
        {
            "name": "Vietnam vs Thailand",
            "description": "Trận giao hữu bóng đá quốc tế.",
            "start_datetime": datetime(2025, 10, 1, 19, 0),
            "end_datetime": datetime(2025, 10, 1, 21, 0),
            "venue_name": "SVĐ Mỹ Đình",
            "location": "Lê Đức Thọ, Nam Từ Liêm, Hà Nội",
            "rules": "Không mang pháo sáng.",
            "authors": "Đội tuyển Việt Nam",
            "producers": "VFF",
            "image_url": "https://res.cloudinary.com/dgqx9xde1/image/upload/v1753612716/vietnam-thailand.jpg",
            "has_seat": True,
            "event_type": EventTypeEnum.THE_THAO
        },
        {
            "name": "Marathon Hà Nội",
            "description": "Giải chạy Marathon toàn thành phố.",
            "start_datetime": datetime(2025, 10, 2, 6, 0),
            "end_datetime": datetime(2025, 10, 2, 12, 0),
            "venue_name": "Hà Nội",
            "location": "Phố cổ - Hồ Gươm",
            "rules": "Đảm bảo sức khỏe, tuân thủ lộ trình.",
            "authors": "Sở Văn hóa - Thể thao Hà Nội",
            "producers": "Sport Media",
            "image_url": "https://res.cloudinary.com/dgqx9xde1/image/upload/v1753612716/marathon.jpg",
            "has_seat": False,
            "event_type": EventTypeEnum.THE_THAO
        },
        {
            "name": "Giải Bóng rổ VBA",
            "description": "Trận đấu bóng rổ VBA hấp dẫn.",
            "start_datetime": datetime(2025, 10, 5, 18, 0),
            "end_datetime": datetime(2025, 10, 5, 20, 0),
            "venue_name": "Nhà thi đấu Phan Đình Phùng",
            "location": "8 Võ Văn Tần, Quận 3, TP.HCM",
            "rules": "Không cổ vũ quá khích.",
            "authors": "Saigon Heat vs Hanoi Buffaloes",
            "producers": "VBA",
            "image_url": "https://res.cloudinary.com/dgqx9xde1/image/upload/v1753612716/vba.jpg",
            "has_seat": True,
            "event_type": EventTypeEnum.THE_THAO
        },
        {
            "name": "Giải Cầu lông Quốc tế",
            "description": "Giải cầu lông mở rộng quy tụ nhiều tay vợt hàng đầu.",
            "start_datetime": datetime(2025, 10, 8, 9, 0),
            "end_datetime": datetime(2025, 10, 8, 17, 0),
            "venue_name": "Nhà thi đấu Cầu Giấy",
            "location": "35 Trần Quý Kiên, Cầu Giấy, Hà Nội",
            "rules": "Không gây ồn ào trong khi thi đấu.",
            "authors": "Liên đoàn Cầu lông Việt Nam",
            "producers": "SportVN",
            "image_url": "https://res.cloudinary.com/dgqx9xde1/image/upload/v1753612716/caulong.jpg",
            "has_seat": True,
            "event_type": EventTypeEnum.THE_THAO
        },
        {
            "name": "Giải Bơi lội Quốc gia",
            "description": "Các VĐV xuất sắc tranh tài ở nhiều nội dung bơi.",
            "start_datetime": datetime(2025, 10, 12, 8, 0),
            "end_datetime": datetime(2025, 10, 12, 16, 0),
            "venue_name": "Cung thể thao dưới nước Mỹ Đình",
            "location": "Lê Đức Thọ, Nam Từ Liêm, Hà Nội",
            "rules": "Không xả rác, giữ vệ sinh hồ bơi.",
            "authors": "Liên đoàn Bơi lội Việt Nam",
            "producers": "VSA",
            "image_url": "https://res.cloudinary.com/dgqx9xde1/image/upload/v1753612716/boiloi.jpg",
            "has_seat": False,
            "event_type": EventTypeEnum.THE_THAO
        },
        {
            "name": "Giải Tennis Quốc tế",
            "description": "Giải tennis có sự góp mặt của nhiều tay vợt nổi tiếng.",
            "start_datetime": datetime(2025, 10, 15, 10, 0),
            "end_datetime": datetime(2025, 10, 15, 18, 0),
            "venue_name": "Sân Tennis Phú Thọ",
            "location": "215 Lý Thường Kiệt, Quận 11, TP.HCM",
            "rules": "Không làm phiền VĐV khi đang thi đấu.",
            "authors": "Liên đoàn Tennis Việt Nam",
            "producers": "VTF",
            "image_url": "https://res.cloudinary.com/dgqx9xde1/image/upload/v1753612716/tennis.jpg",
            "has_seat": True,
            "event_type": EventTypeEnum.THE_THAO
        },
        {
            "name": "Giải Võ thuật MMA",
            "description": "Trận đấu MMA đỉnh cao giữa các võ sĩ hàng đầu.",
            "start_datetime": datetime(2025, 10, 20, 19, 0),
            "end_datetime": datetime(2025, 10, 20, 22, 0),
            "venue_name": "Nhà thi đấu Quân khu 7",
            "location": "202 Hoàng Văn Thụ, Tân Bình, TP.HCM",
            "rules": "Không kích động bạo lực.",
            "authors": "MMA Fighters",
            "producers": "MMA VN",
            "image_url": "https://res.cloudinary.com/dgqx9xde1/image/upload/v1753612716/mma.jpg",
            "has_seat": True,
            "event_type": EventTypeEnum.THE_THAO
        },
        {
            "name": "Giải Đua xe đạp TP.HCM",
            "description": "Giải đua xe đạp vòng quanh thành phố.",
            "start_datetime": datetime(2025, 10, 25, 7, 0),
            "end_datetime": datetime(2025, 10, 25, 11, 0),
            "venue_name": "TP.HCM",
            "location": "Quận 1 - Quận 7",
            "rules": "Không chạy sai lộ trình.",
            "authors": "Liên đoàn Xe đạp VN",
            "producers": "Cycling HCMC",
            "image_url": "https://res.cloudinary.com/dgqx9xde1/image/upload/v1753612716/xe_dap.jpg",
            "has_seat": False,
            "event_type": EventTypeEnum.THE_THAO
        },
        {
            "name": "Giải Cờ vua Trẻ",
            "description": "Giải cờ vua dành cho các tài năng trẻ.",
            "start_datetime": datetime(2025, 10, 28, 8, 0),
            "end_datetime": datetime(2025, 10, 28, 17, 0),
            "venue_name": "Cung Văn hóa Lao động",
            "location": "55B Nguyễn Thị Minh Khai, Quận 1, TP.HCM",
            "rules": "Giữ trật tự khi thi đấu.",
            "authors": "Liên đoàn Cờ Việt Nam",
            "producers": "ChessVN",
            "image_url": "https://res.cloudinary.com/dgqx9xde1/image/upload/v1753612716/covua.jpg",
            "has_seat": True,
            "event_type": EventTypeEnum.THE_THAO
        },
        {
            "name": "Giải Thể hình Quốc gia",
            "description": "Cuộc thi thể hình chuyên nghiệp.",
            "start_datetime": datetime(2025, 10, 30, 18, 0),
            "end_datetime": datetime(2025, 10, 30, 21, 0),
            "venue_name": "Nhà thi đấu Tân Bình",
            "location": "448 Hoàng Văn Thụ, Tân Bình, TP.HCM",
            "rules": "Không la ó, gây mất trật tự.",
            "authors": "Liên đoàn Thể hình VN",
            "producers": "Fitness VN",
            "image_url": "https://res.cloudinary.com/dgqx9xde1/image/upload/v1753612716/thehinh.jpg",
            "has_seat": True,
            "event_type": EventTypeEnum.THE_THAO
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
            event_format=EventFormatEnum.OFFLINE,
            event_type=data.get("event_type", EventTypeEnum.NGHE_THUAT),  # lấy đúng loại
            organizer_id=organizer.id,
            status=StatusEventEnum.DA_DUYET
        )
        db.session.add(event)
        db.session.flush()  # để có event.id

        offline = EventOffline(
            event_id=event.id,
            venue_name=data["venue_name"],
            location=data["location"],
            has_seat=data.get("has_seat", False)
        )
        db.session.add(offline)

    db.session.commit()

def seed_event_online():
    online_events_data = [
        {
            "name": "Hội Thảo Công Nghệ Blockchain",
            "description": "Buổi hội thảo trực tuyến về blockchain và các ứng dụng thực tiễn.",
            "start_datetime": datetime(2025, 9, 10, 9, 0),
            "end_datetime": datetime(2025, 9, 10, 12, 0),
            "rules": "Không chia sẻ link cho người ngoài. Giữ thái độ văn minh.",
            "authors": "TS. Lê Văn A",
            "producers": "TechTalk Vietnam",
            "image_url": "https://res.cloudinary.com/dgqx9xde1/image/upload/v1753612715/acoustic_akxfdk.jpg",
            "livestream_url": "https://zoom.us/j/1234567890"
        },
        {
            "name": "Workshop UX/UI Design",
            "description": "Khóa học online giới thiệu về UX/UI trong thiết kế ứng dụng.",
            "start_datetime": datetime(2025, 9, 20, 14, 0),
            "end_datetime": datetime(2025, 9, 20, 17, 0),
            "rules": "Chuẩn bị máy tính để thực hành.",
            "authors": "Nguyễn Minh Hòa",
            "producers": "UXVN",
            "image_url": "https://res.cloudinary.com/dgqx9xde1/image/upload/v1753613002/uiux.jpg",
            "livestream_url": "https://meet.google.com/uxui123"
        },
        {
            "name": "Khóa Học Lập Trình Python Cơ Bản",
            "description": "Khóa học online cho người mới bắt đầu với Python.",
            "start_datetime": datetime(2025, 8, 22, 19, 0),
            "end_datetime": datetime(2025, 8, 22, 21, 0),
            "rules": "Không ghi hình bài giảng.",
            "authors": "Trần Văn B",
            "producers": "CodeAcademy VN",
            "image_url": "https://res.cloudinary.com/dgqx9xde1/image/upload/v1753613003/python.jpg",
            "livestream_url": "https://zoom.us/j/9876543210"
        },
        {
            "name": "Talkshow Start-up 2025",
            "description": "Chia sẻ từ các founder startup công nghệ Việt.",
            "start_datetime": datetime(2025, 10, 5, 10, 0),
            "end_datetime": datetime(2025, 10, 5, 12, 0),
            "rules": "Không spam trong phòng chat.",
            "authors": "Nguyễn Thị Mai, CEO ABC",
            "producers": "Venture Hub",
            "image_url": "https://res.cloudinary.com/dgqx9xde1/image/upload/v1753613004/startup.jpg",
            "livestream_url": "https://youtube.com/live/abc123"
        },
        {
            "name": "Concert Online - EDM Night",
            "description": "Đêm nhạc EDM trực tuyến với các DJ hàng đầu.",
            "start_datetime": datetime(2025, 11, 1, 20, 0),
            "end_datetime": datetime(2025, 11, 1, 23, 0),
            "rules": "Cấm ghi âm, ghi hình.",
            "authors": "DJ Wang, DJ Dero",
            "producers": "MusicHub",
            "image_url": "https://res.cloudinary.com/dgqx9xde1/image/upload/v1753613005/edm.jpg",
            "livestream_url": "https://twitch.tv/edmnight"
        },
        {
            "name": "Khóa Học Digital Marketing",
            "description": "Giới thiệu tổng quan về SEO, Ads và Content Marketing.",
            "start_datetime": datetime(2025, 9, 18, 18, 0),
            "end_datetime": datetime(2025, 9, 18, 20, 0),
            "rules": "Tham gia đúng giờ.",
            "authors": "Phạm Văn C",
            "producers": "MarketingPro",
            "image_url": "https://res.cloudinary.com/dgqx9xde1/image/upload/v1753613006/marketing.jpg",
            "livestream_url": "https://meet.google.com/mkt123"
        },
        {
            "name": "Khóa Học AI Cơ Bản",
            "description": "Giới thiệu trí tuệ nhân tạo và các ứng dụng.",
            "start_datetime": datetime(2025, 8, 28, 19, 0),
            "end_datetime": datetime(2025, 8, 28, 21, 30),
            "rules": "Không chia sẻ tài liệu ra ngoài.",
            "authors": "TS. John Doe",
            "producers": "AI4VN",
            "image_url": "https://res.cloudinary.com/dgqx9xde1/image/upload/v1753613007/ai.jpg",
            "livestream_url": "https://zoom.us/j/ai2025"
        },
        {
            "name": "Khai Giảng Khóa IELTS Online",
            "description": "Khóa học IELTS online cùng giảng viên bản ngữ.",
            "start_datetime": datetime(2025, 9, 1, 18, 0),
            "end_datetime": datetime(2025, 9, 1, 20, 0),
            "rules": "Chuẩn bị tài liệu học trước.",
            "authors": "Mr. Peter",
            "producers": "IELTS Academy",
            "image_url": "https://res.cloudinary.com/dgqx9xde1/image/upload/v1753613008/ielts.jpg",
            "livestream_url": "https://zoom.us/j/ielts2025"
        },
        {
            "name": "Workshop Kỹ Năng Thuyết Trình",
            "description": "Học kỹ năng thuyết trình chuyên nghiệp trực tuyến.",
            "start_datetime": datetime(2025, 10, 12, 19, 0),
            "end_datetime": datetime(2025, 10, 12, 21, 0),
            "rules": "Bật camera khi thuyết trình.",
            "authors": "Nguyễn Văn D",
            "producers": "SoftSkillVN",
            "image_url": "https://res.cloudinary.com/dgqx9xde1/image/upload/v1753613009/presentation.jpg",
            "livestream_url": "https://meet.google.com/speak123"
        },
        {
            "name": "Livestream Giới Thiệu Sản Phẩm Apple 2025",
            "description": "Sự kiện Apple trực tuyến ra mắt sản phẩm mới.",
            "start_datetime": datetime(2025, 9, 20, 0, 0),
            "end_datetime": datetime(2025, 9, 20, 2, 0),
            "rules": "Chỉ dành cho người đăng ký trước.",
            "authors": "Apple Inc.",
            "producers": "Apple Event",
            "image_url": "https://res.cloudinary.com/dgqx9xde1/image/upload/v1753613010/appleevent.jpg",
            "livestream_url": "https://apple.com/apple-events"
        }
    ]

    organizer = EventOrganizer.query.filter_by(fullname="Trần Bảo Ngọc").first()

    for data in online_events_data:
        event = Event(
            name=data["name"],
            description=data["description"],
            start_datetime=data["start_datetime"],
            end_datetime=data["end_datetime"],
            rules=data["rules"],
            authors=data["authors"],
            producers=data["producers"],
            image_url=data["image_url"],
            event_format=EventFormatEnum.ONLINE,
            event_type=EventTypeEnum.KHAC,
            organizer_id=organizer.id,
            status=StatusEventEnum.DA_DUYET
        )
        db.session.add(event)
        db.session.flush()  # lấy event.id

        online = EventOnline(
            event_id=event.id,
            livestream_url=data["livestream_url"]
        )
        db.session.add(online)

    db.session.commit()

def seed_ticket_type():
    ticket_types = [
        TicketType(
            name='Vé Thường',
            price=2000,
            quantity=50,
            event_id=1,
            benefits="Đảm bảo quyền lợi tham gia sự kiện|Ghế ngồi sắp xếp ngẫu nhiên|Ghế ngồi xa sân khấu"
        ),
        TicketType(
            name='Vé VIP',
            price=5000,
            quantity=50,
            event_id=1,
            benefits="Khu vực checkin riêng, không phải xếp hàng|Ghế ngồi gần sân khấu, quà tặng đặc biệt|Dịch vụ ăn uống, quà tặng, giao lưu nghệ sĩ",
            requires_seat=True
        ),
        TicketType(
            name='Vé Standing',
            price=3000,
            quantity=50,
            event_id=2,
            benefits="Khu vực đứng gần sân khấu|Không giới hạn di chuyển khu vực standing|Trải nghiệm âm thanh sống động"
        ),
        TicketType(
            name='Vé VIP',
            price=6500,
            quantity=50,
            event_id=2,
            benefits="Khu vực checkin riêng, không phải xếp hàng|Ghế ngồi gần sân khấu, quà tặng đặc biệt|Dịch vụ ăn uống, quà tặng, giao lưu nghệ sĩ"
        ),
        TicketType(
            name='Vé Thường',
            price=2000,
            quantity=50,
            event_id=3,
            benefits="Đảm bảo quyền lợi tham gia sự kiện|Ghế ngồi sắp xếp ngẫu nhiên|Ghế ngồi xa sân khấu"
        ),
        TicketType(
            name='Vé Premium',
            price=4000,
            quantity=50,
            event_id=3,
            benefits="Ghế ngồi ở khu vực trung tâm|Tặng voucher đồ uống|Có cơ hội chụp hình lưu niệm"
        )
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
        seed_event_online()  # 10 sự kiện online
        seed_ticket_type()

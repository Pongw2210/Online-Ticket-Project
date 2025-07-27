import hashlib
from datetime import datetime
from sqlalchemy import inspect
from app import create_app, db
from app.data.models import Admin, User, Customer, UserEnum, EventOrganizer,EventOffline,TicketType

app = create_app()

def seed_admin_user():
    admin1 = Admin(fullname="Đặng Mỹ Ngọc", email="dmn@gmail.com", gender="Nữ")
    db.session.add(admin1)
    uAdmin1 = User(username="userAdmin", password=str(hashlib.md5("123".encode('utf-8')).hexdigest()),
                   avatar="https://res.cloudinary.com/dgqx9xde1/image/upload/v1744900055/User2_qjswcy.webp",
                   role=UserEnum.ADMIN)
    uAdmin1.admin = admin1
    db.session.add(uAdmin1)
    db.session.commit()

def seed_customer_user():
    cus1 = Customer(fullname="Nguyễn Ngọc Anh", email="nna@gmail.com", gender="Nữ", dob=datetime(2000, 1, 1),
                    number_phone="0987654321")
    db.session.add(cus1)
    ucus1 = User(username="userKhachHang", password=str(hashlib.md5("123".encode('utf-8')).hexdigest()),
                 avatar="https://res.cloudinary.com/dgqx9xde1/image/upload/v1744900183/User3_byutxj.jpg",
                 role=UserEnum.KHACH_HANG)
    ucus1.customer = cus1
    db.session.add(ucus1)
    db.session.commit()

def seed_event_organizer_user():
    event_organizer1 = EventOrganizer(fullname="Trần Bảo Ngọc", email="tbn@gmail.com", gender="Nữ")
    db.session.add(event_organizer1)
    uEvent_organizer1 = User(username="userNguoiToChuc",
                             password=str(hashlib.md5("123".encode('utf-8')).hexdigest()),
                             role=UserEnum.NGUOI_TO_CHUC)
    uEvent_organizer1.event_organizer = event_organizer1
    db.session.add(uEvent_organizer1)
    db.session.commit()

def seed_events():
    events = [
        EventOffline(
            name='Gốm Show - Hà Nội',
            description='Gốm Show là dự án nghệ thuật âm nhạc sáng tạo, lấy cảm hứng từ gốm truyền thống Việt Nam...',
            start_datetime=datetime(2025, 7, 31, 19, 30),
            end_datetime=datetime(2025, 7, 31, 21, 30),
            venue_name='Nhà hát Lớn Hà Nội',
            location='1 Tràng Tiền, Phan Chu Trinh, Hoàn Kiếm, Hà Nội',
            rules='Không mang vũ khí, chất cấm, không quay phim...',
            authors='Đạo diễn Nguyễn Văn A, Biên đạo Trần Văn B',
            producers='SKY SOUND PRODUCTION, Nhà hát Lớn Hà Nội',
            image_url='https://res.cloudinary.com/dgqx9xde1/image/upload/v1753612716/gomshow_spfsbk.jpg'
        ),
        EventOffline(
            name='Hòa Nhạc Mùa Thu',
            description='Chương trình âm nhạc cổ điển được trình diễn bởi dàn nhạc giao hưởng quốc gia...',
            start_datetime=datetime(2025, 9, 5, 19, 0),
            end_datetime=datetime(2025, 9, 5, 21, 0),
            venue_name='Nhà hát Lớn TP.HCM',
            location='7 Công Trường Lam Sơn, Bến Nghé, Quận 1, TP.HCM',
            rules='Trang phục lịch sự.\nKhông mang đồ ăn, nước uống vào khán phòng.\nVé này không dành cho trẻ em dưới 8 tuổi...',
            authors='NSƯT Lê Hồng Sơn',
            producers='Dàn nhạc giao hưởng Quốc gia',
            image_url='https://res.cloudinary.com/dgqx9xde1/image/upload/v1753612717/hoa-nhac-mua-thu_r3vwtt.jpg'
        ),
        EventOffline(
            name='Live Concert Sơn Tùng M-TP',
            description='Đêm nhạc "Sky Tour" là sự kiện âm nhạc đỉnh cao của ca sĩ Sơn Tùng M-TP...',
            start_datetime=datetime(2025, 8, 12, 20, 0),
            end_datetime=datetime(2025, 8, 12, 22, 30),
            venue_name='Sân vận động Mỹ Đình',
            location='Lê Đức Thọ, Nam Từ Liêm, Hà Nội',
            rules='Trang phục lịch sự.\nKhông mang đồ ăn, nước uống vào khán phòng.\nVé này không dành cho trẻ em dưới 8 tuổi...',
            authors='Sơn Tùng M-TP',
            producers='M-TP Entertainment',
            image_url='https://res.cloudinary.com/dgqx9xde1/image/upload/v1753612717/mtp-live_aelu1w.jpg'
        ),
        EventOffline(
            name='Đêm Nhạc Trịnh – Gọi Tên Bốn Mùa',
            description='Một đêm nhạc lắng đọng với những bản tình ca bất hủ của nhạc sĩ Trịnh Công Sơn...',
            start_datetime=datetime(2025, 8, 25, 20, 0),
            end_datetime=datetime(2025, 8, 25, 22, 0),
            venue_name='Nhà hát Hòa Bình',
            location='240 Đường 3/2, Quận 10, TP.HCM',
            rules='Trang phục lịch sự.\nKhông mang đồ ăn, nước uống vào khán phòng...',
            authors='Ban nhạc Mùa Thu, Ca sĩ Hồng Nhung, Ca sĩ Đức Tuấn',
            producers='Công ty Truyền Thông Mưa',
            image_url='https://res.cloudinary.com/dgqx9xde1/image/upload/v1753612716/demnhactrinh_wdtcul.jpg'
        ),
        EventOffline(
            name='Sân Khấu Hài – Tám Chuyện Cuối Tuần',
            description='Một buổi biểu diễn hài kịch vui nhộn với sự tham gia của các nghệ sĩ hài nổi tiếng...',
            start_datetime=datetime(2025, 8, 17, 19, 30),
            end_datetime=datetime(2025, 8, 17, 21, 30),
            venue_name='Nhà hát Kịch Sài Gòn',
            location='30 Trần Hưng Đạo, Quận 1, TP.HCM',
            rules='Trang phục lịch sự.\nKhông mang đồ ăn, nước uống vào khán phòng...\nVé không hoàn tiền sau khi mua...',
            authors='Nhóm Hài Thứ Bảy, MC Đại Nghĩa',
            producers='Công ty Giải Trí Cười Vui',
            image_url='https://res.cloudinary.com/dgqx9xde1/image/upload/v1753612716/haicuoi_crzki5.jpg'
        ),
        EventOffline(
            name='Gala Hài Kịch 2025',
            description='Sự kiện quy tụ dàn nghệ sĩ hài nổi tiếng như Trấn Thành, Việt Hương, Trường Giang… với những tiểu phẩm đặc sắc, hài hước và đầy ý nghĩa. Không chỉ mang tiếng cười, Gala còn gửi gắm thông điệp xã hội nhân văn.',
            start_datetime=datetime(2025, 11, 25, 18, 30),
            end_datetime=datetime(2025, 11, 25, 21, 30),
            venue_name='Nhà hát Bến Thành',
            location='6 Mạc Đĩnh Chi, Bến Nghé, Quận 1, TP.HCM',
            rules='Trang phục lịch sự.\nKhông mang đồ ăn, nước uống vào khán phòng.\nVé này không dành cho trẻ em dưới 8 tuổi.\nVui lòng không quay phim, chụp ảnh trong suốt chương trình.\nVé sẽ hết hiệu lực sau 15 phút kể từ thời điểm chương trình biểu diễn bắt đầu.',
            authors='Trấn Thành, Việt Hương',
            producers='Hài TV & Showbiz Việt',
            image_url='https://res.cloudinary.com/dgqx9xde1/image/upload/v1753612716/gala-hai_l9vlnz.jpg'
        ),
        EventOffline(
            name='Kịch Trinh Thám: "Lưới Trời"',
            description='Vở kịch trinh thám đầy kịch tính với nội dung bất ngờ, lối diễn xuất chuyên nghiệp cùng âm thanh ánh sáng đỉnh cao. "Lưới Trời" đưa khán giả vào một hành trình phá án nghẹt thở qua từng hồi kịch.',
            start_datetime=datetime(2025, 10, 30, 19, 0),
            end_datetime=datetime(2025, 10, 30, 21, 0),
            venue_name='Sân khấu kịch Idecaf',
            location='28 Lê Thánh Tôn, Quận 1, TP.HCM',
            rules='Trang phục lịch sự.\nKhông mang đồ ăn, nước uống vào khán phòng.\nVé này không dành cho trẻ em dưới 8 tuổi.\nVui lòng không quay phim, chụp ảnh trong suốt chương trình.\nVé sẽ hết hiệu lực sau 15 phút kể từ thời điểm chương trình biểu diễn bắt đầu.',
            authors='Đạo diễn Nguyễn Ngọc Bảo',
            producers='Nhà hát kịch Idecaf',
            image_url='https://res.cloudinary.com/dgqx9xde1/image/upload/v1753612717/kich-luoi-troi_nwzh6p.jpg'
        ),
        EventOffline(
            name='Rap Việt All Stars',
            description='Sự kiện âm nhạc hoành tráng quy tụ những rapper nổi bật nhất từ chương trình Rap Việt như Binz, Karik, Wowy, Rhymastic... với màn trình diễn bùng nổ, hệ thống sân khấu cực khủng và hàng chục nghìn khán giả.',
            start_datetime=datetime(2025, 12, 10, 19, 30),
            end_datetime=datetime(2025, 12, 10, 23, 0),
            venue_name='Sân vận động Thống Nhất',
            location='30 Nguyễn Kim, Quận 10, TP.HCM',
            rules='Trang phục lịch sự.\nKhông mang đồ ăn, nước uống vào khán phòng.\nVé này không dành cho trẻ em dưới 8 tuổi.\nVui lòng không quay phim, chụp ảnh trong suốt chương trình.\nVé sẽ hết hiệu lực sau 15 phút kể từ thời điểm chương trình biểu diễn bắt đầu.',
            authors='Binz, Wowy, Rhymastic',
            producers='VieON, Rap Việt Production',
            image_url='https://res.cloudinary.com/dgqx9xde1/image/upload/v1753612717/rapviet_pxr0ye.jpg'
        ),
        EventOffline(
            name='Triển Lãm Tranh 3D Quốc Tế',
            description='Một thế giới nghệ thuật sống động qua những bức tranh 3D ấn tượng, mang lại trải nghiệm thị giác độc đáo. Khách tham quan được phép tương tác, chụp ảnh với các tác phẩm nghệ thuật.',
            start_datetime=datetime(2025, 10, 1, 8, 0),
            end_datetime=datetime(2025, 10, 5, 18, 0),
            venue_name='Trung tâm triển lãm SECC',
            location='799 Nguyễn Văn Linh, Quận 7, TP.HCM',
            rules='Trang phục lịch sự.\nKhông mang đồ ăn, nước uống vào khán phòng.\nVé này không dành cho trẻ em dưới 8 tuổi.\nVui lòng không quay phim, chụp ảnh trong suốt chương trình.\nVé sẽ hết hiệu lực sau 15 phút kể từ thời điểm chương trình biểu diễn bắt đầu.',
            authors='Tổ chức nghệ thuật 3D Asia',
            producers='SECC phối hợp Bộ Văn hóa',
            image_url='https://res.cloudinary.com/dgqx9xde1/image/upload/v1753612717/trienlam3d_gsqm4t.jpg'
        ),
        EventOffline(
            name='Thơ - Nhạc Trịnh Công Sơn',
            description='Đêm nhạc tưởng nhớ cố nhạc sĩ Trịnh Công Sơn với các tác phẩm bất hủ, do các nghệ sĩ gạo cội và thế hệ trẻ thể hiện. Không gian âm nhạc nhẹ nhàng, sâu lắng giúp khán giả lắng đọng cảm xúc.',
            start_datetime=datetime(2025, 4, 1, 19, 0),
            end_datetime=datetime(2025, 4, 1, 21, 0),
            venue_name='Nhà hát Hòa Bình',
            location='240 Đường 3 Tháng 2, Quận 10, TP.HCM',
            rules='Trang phục lịch sự.\nKhông mang đồ ăn, nước uống vào khán phòng.\nVé này không dành cho trẻ em dưới 8 tuổi.\nVui lòng không quay phim, chụp ảnh trong suốt chương trình.\nVé sẽ hết hiệu lực sau 15 phút kể từ thời điểm chương trình biểu diễn bắt đầu.',
            authors='Hồng Nhung, Đức Tuấn',
            producers='Gia đình Trịnh Công Sơn & Nhà hát Hòa Bình',
            image_url='https://res.cloudinary.com/dgqx9xde1/image/upload/v1753612718/trinhcongson_pu5pmv.jpg'
        ),
        EventOffline(
            name='Hội Thảo Công Nghệ AI 2025',
            description=(
                'Hội thảo quy tụ các chuyên gia AI hàng đầu Việt Nam và quốc tế, cập nhật xu hướng công nghệ mới nhất '
                'về trí tuệ nhân tạo, machine learning, data science cùng các ứng dụng thực tế tại Việt Nam.'
            ),
            start_datetime=datetime(2025, 9, 15, 9, 0),
            end_datetime=datetime(2025, 9, 15, 17, 0),
            venue_name='Trung tâm Hội nghị Quốc gia',
            location='Cổng số 1 Đại lộ Thăng Long, Nam Từ Liêm, Hà Nội',
            rules=(
                'Trang phục lịch sự.\n'
                'Không mang đồ ăn, nước uống vào khán phòng.\n'
                'Vé này không dành cho trẻ em dưới 8 tuổi.\n'
                'Vui lòng không quay phim, chụp ảnh trong suốt chương trình.\n'
                'Vé sẽ hết hiệu lực sau 15 phút kể từ thời điểm chương trình biểu diễn bắt đầu.'
            ),
            authors='TS. Nguyễn Văn A, Prof. John Doe',
            producers='Bộ KH&CN & TechTalks Vietnam',
            image_url='https://res.cloudinary.com/dgqx9xde1/image/upload/v1753612715/ai-conference_kvlkfl.jpg'
        ),
        EventOffline(
            name='Đêm Nhạc Acoustic "Góc Phố Xưa"',
            description=(
                'Sự kiện âm nhạc dành cho những tâm hồn yêu sự bình yên, hoài niệm. Với dàn nhạc acoustic, khán giả được '
                'thưởng thức những bản ballad, nhạc xưa trong không gian cafe ấm cúng, gần gũi.'
            ),
            start_datetime=datetime(2025, 8, 20, 20, 0),
            end_datetime=datetime(2025, 8, 20, 22, 0),
            venue_name='Trixie Cafe & Lounge',
            location='165 Thái Hà, Đống Đa, Hà Nội',
            rules=(
                'Trang phục lịch sự.\n'
                'Không mang đồ ăn, nước uống vào khán phòng.\n'
                'Vé này không dành cho trẻ em dưới 8 tuổi.\n'
                'Vui lòng không quay phim, chụp ảnh trong suốt chương trình.\n'
                'Vé sẽ hết hiệu lực sau 15 phút kể từ thời điểm chương trình biểu diễn bắt đầu.'
            ),
            authors='Minh Vương M4U, Trang',
            producers='Trixie Music Group',
            image_url='https://res.cloudinary.com/dgqx9xde1/image/upload/v1753612715/acoustic_akxfdk.jpg'
        )
    ]
    db.session.add_all(events)
    db.session.commit()

def seed_ticket_type():
    ticket_types = [
        TicketType(name='Vé Thường', price=250000, event_id=1),
        TicketType(name='Vé VIP', price=500000, event_id=1),
        TicketType(name='Vé Standing', price=300000, event_id=2),
        TicketType(name='Vé VIP', price=650000, event_id=2),
        TicketType(name='Vé Thường', price=200000, event_id=3),
        TicketType(name='Vé Premium', price=400000, event_id=3),
    ]

    db.session.add_all(ticket_types)
    db.session.commit()

if __name__ == "__main__":
    with app.app_context():
        # db.drop_all()
        # db.create_all()

        # seed_customer_user()
        # seed_admin_user()
        # seed_event_organizer_user()

        seed_events()
        seed_ticket_type()











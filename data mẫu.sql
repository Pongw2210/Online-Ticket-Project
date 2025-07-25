-- Thêm sự kiện
INSERT INTO event (
    name, description, date, location, location_detail, rules, authors, producers, image_url
) VALUES 
(   'Gốm Show - Hà Nội',
    'Gốm Show là dự án nghệ thuật âm nhạc sáng tạo, lấy cảm hứng từ gốm truyền thống Việt Nam...',
    '19:30 - 21:30, 31 Tháng 07, 2025',
    'Nhà hát Lớn Hà Nội',
    '1 Tràng Tiền, Phan Chu Trinh, Hoàn Kiếm, Hà Nội',
    'Không mang vũ khí, chất cấm, không quay phim...',
    'Đạo diễn Nguyễn Văn A, Biên đạo Trần Văn B',
    'SKY SOUND PRODUCTION, Nhà hát Lớn Hà Nội',
    'images/gomshow.jpg'),

('Hòa Nhạc Mùa Thu', 
 'Chương trình âm nhạc cổ điển được trình diễn bởi dàn nhạc giao hưởng quốc gia, mang đến một trải nghiệm nghệ thuật đỉnh cao với các tác phẩm bất hủ từ Beethoven, Mozart và nhiều nhà soạn nhạc vĩ đại khác. Sự kết hợp hài hòa giữa âm nhạc và không gian nhà hát sang trọng hứa hẹn tạo nên một buổi tối đáng nhớ.',
 '19:00 - 21:00, 05/09/2025', 
 'Nhà hát Lớn TP.HCM', 
 '7 Công Trường Lam Sơn, Bến Nghé, Quận 1, TP.HCM', 
 'Trang phục lịch sự.\nKhông mang đồ ăn, nước uống vào khán phòng.\nVé này không dành cho trẻ em dưới 8 tuổi.\nVui lòng không quay phim, chụp ảnh trong suốt chương trình.\nVé sẽ hết hiệu lực sau 15 phút kể từ thời điểm chương trình biểu diễn bắt đầu.',
 'NSƯT Lê Hồng Sơn', 
 'Dàn nhạc giao hưởng Quốc gia', 
 'images/hoa-nhac-mua-thu.jpg'),


('Live Concert Sơn Tùng M-TP', 
 'Đêm nhạc "Sky Tour" là sự kiện âm nhạc đỉnh cao của ca sĩ Sơn Tùng M-TP, với dàn dựng sân khấu hiện đại, âm thanh ánh sáng cực chất và hàng loạt bản hit làm nên tên tuổi của anh. Chương trình còn có sự tham gia của nhiều khách mời đặc biệt.',
 '20:00 - 22:30, 12/08/2025', 
 'Sân vận động Mỹ Đình', 
 'Lê Đức Thọ, Nam Từ Liêm, Hà Nội', 
 'Trang phục lịch sự.\nKhông mang đồ ăn, nước uống vào khán phòng.\nVé này không dành cho trẻ em dưới 8 tuổi.\nVui lòng không quay phim, chụp ảnh trong suốt chương trình.\nVé sẽ hết hiệu lực sau 15 phút kể từ thời điểm chương trình biểu diễn bắt đầu.',
 'Sơn Tùng M-TP', 
 'M-TP Entertainment', 
 'images/mtp-live.jpg'),

-- 3
('Gala Hài Kịch 2025', 
 'Sự kiện quy tụ dàn nghệ sĩ hài nổi tiếng như Trấn Thành, Việt Hương, Trường Giang… với những tiểu phẩm đặc sắc, hài hước và đầy ý nghĩa. Không chỉ mang tiếng cười, Gala còn gửi gắm thông điệp xã hội nhân văn.',
 '18:30 - 21:30, 25/11/2025', 
 'Nhà hát Bến Thành', 
 '6 Mạc Đĩnh Chi, Bến Nghé, Quận 1, TP.HCM', 
 'Trang phục lịch sự.\nKhông mang đồ ăn, nước uống vào khán phòng.\nVé này không dành cho trẻ em dưới 8 tuổi.\nVui lòng không quay phim, chụp ảnh trong suốt chương trình.\nVé sẽ hết hiệu lực sau 15 phút kể từ thời điểm chương trình biểu diễn bắt đầu.',
 'Trấn Thành, Việt Hương', 
 'Hài TV & Showbiz Việt', 
 'images/gala-hai.jpg'),

-- 4
('Kịch Trinh Thám: "Lưới Trời"', 
 'Vở kịch trinh thám đầy kịch tính với nội dung bất ngờ, lối diễn xuất chuyên nghiệp cùng âm thanh ánh sáng đỉnh cao. "Lưới Trời" đưa khán giả vào một hành trình phá án nghẹt thở qua từng hồi kịch.',
 '19:00 - 21:00, 30/10/2025', 
 'Sân khấu kịch Idecaf', 
 '28 Lê Thánh Tôn, Quận 1, TP.HCM', 
 'Trang phục lịch sự.\nKhông mang đồ ăn, nước uống vào khán phòng.\nVé này không dành cho trẻ em dưới 8 tuổi.\nVui lòng không quay phim, chụp ảnh trong suốt chương trình.\nVé sẽ hết hiệu lực sau 15 phút kể từ thời điểm chương trình biểu diễn bắt đầu.',
 'Đạo diễn Nguyễn Ngọc Bảo', 
 'Nhà hát kịch Idecaf', 
 'images/kich-luoi-troi.jpg'),

-- 5
('Rap Việt All Stars', 
 'Sự kiện âm nhạc hoành tráng quy tụ những rapper nổi bật nhất từ chương trình Rap Việt như Binz, Karik, Wowy, Rhymastic... với màn trình diễn bùng nổ, hệ thống sân khấu cực khủng và hàng chục nghìn khán giả.',
 '19:30 - 23:00, 10/12/2025', 
 'Sân vận động Thống Nhất', 
 '30 Nguyễn Kim, Quận 10, TP.HCM', 
 'Trang phục lịch sự.\nKhông mang đồ ăn, nước uống vào khán phòng.\nVé này không dành cho trẻ em dưới 8 tuổi.\nVui lòng không quay phim, chụp ảnh trong suốt chương trình.\nVé sẽ hết hiệu lực sau 15 phút kể từ thời điểm chương trình biểu diễn bắt đầu.',
 'Binz, Wowy, Rhymastic', 
 'VieON, Rap Việt Production', 
 'images/rapviet.jpg'),

-- 6
('Triển Lãm Tranh 3D Quốc Tế', 
 'Một thế giới nghệ thuật sống động qua những bức tranh 3D ấn tượng, mang lại trải nghiệm thị giác độc đáo. Khách tham quan được phép tương tác, chụp ảnh với các tác phẩm nghệ thuật.',
 '08:00 - 18:00, 01-05/10/2025', 
 'Trung tâm triển lãm SECC', 
 '799 Nguyễn Văn Linh, Quận 7, TP.HCM', 
 'Trang phục lịch sự.\nKhông mang đồ ăn, nước uống vào khán phòng.\nVé này không dành cho trẻ em dưới 8 tuổi.\nVui lòng không quay phim, chụp ảnh trong suốt chương trình.\nVé sẽ hết hiệu lực sau 15 phút kể từ thời điểm chương trình biểu diễn bắt đầu.',
 'Tổ chức nghệ thuật 3D Asia', 
 'SECC phối hợp Bộ Văn hóa', 
 'images/trienlam3d.jpg'),

-- 7
('Thơ - Nhạc Trịnh Công Sơn', 
 'Đêm nhạc tưởng nhớ cố nhạc sĩ Trịnh Công Sơn với các tác phẩm bất hủ, do các nghệ sĩ gạo cội và thế hệ trẻ thể hiện. Không gian âm nhạc nhẹ nhàng, sâu lắng giúp khán giả lắng đọng cảm xúc.',
 '19:00 - 21:00, 01/04/2025', 
 'Nhà hát Hòa Bình', 
 '240 Đường 3 Tháng 2, Quận 10, TP.HCM', 
 'Trang phục lịch sự.\nKhông mang đồ ăn, nước uống vào khán phòng.\nVé này không dành cho trẻ em dưới 8 tuổi.\nVui lòng không quay phim, chụp ảnh trong suốt chương trình.\nVé sẽ hết hiệu lực sau 15 phút kể từ thời điểm chương trình biểu diễn bắt đầu.',
 'Hồng Nhung, Đức Tuấn', 
 'Gia đình Trịnh Công Sơn & Nhà hát Hòa Bình', 
 'images/trinhcongson.jpg'),

-- 8
('Hội Thảo Công Nghệ AI 2025', 
 'Hội thảo quy tụ các chuyên gia AI hàng đầu Việt Nam và quốc tế, cập nhật xu hướng công nghệ mới nhất về trí tuệ nhân tạo, machine learning, data science cùng các ứng dụng thực tế tại Việt Nam.',
 '09:00 - 17:00, 15/09/2025', 
 'Trung tâm Hội nghị Quốc gia', 
 'Cổng số 1 Đại lộ Thăng Long, Nam Từ Liêm, Hà Nội', 
 'Trang phục lịch sự.\nKhông mang đồ ăn, nước uống vào khán phòng.\nVé này không dành cho trẻ em dưới 8 tuổi.\nVui lòng không quay phim, chụp ảnh trong suốt chương trình.\nVé sẽ hết hiệu lực sau 15 phút kể từ thời điểm chương trình biểu diễn bắt đầu.',
 'TS. Nguyễn Văn A, Prof. John Doe', 
 'Bộ KH&CN & TechTalks Vietnam', 
 'images/ai-conference.jpg'),

-- 9
('Đêm Nhạc Acoustic "Góc Phố Xưa"', 
 'Sự kiện âm nhạc dành cho những tâm hồn yêu sự bình yên, hoài niệm. Với dàn nhạc acoustic, khán giả được thưởng thức những bản ballad, nhạc xưa trong không gian cafe ấm cúng, gần gũi.',
 '20:00 - 22:00, 20/08/2025', 
 'Trixie Cafe & Lounge', 
 '165 Thái Hà, Đống Đa, Hà Nội', 
 'Trang phục lịch sự.\nKhông mang đồ ăn, nước uống vào khán phòng.\nVé này không dành cho trẻ em dưới 8 tuổi.\nVui lòng không quay phim, chụp ảnh trong suốt chương trình.\nVé sẽ hết hiệu lực sau 15 phút kể từ thời điểm chương trình biểu diễn bắt đầu.',
 'Minh Vương M4U, Trang', 
 'Trixie Music Group', 
 'images/acoustic.jpg');
 
 INSERT INTO event (name, description, date, location, location_detail, rules, authors, producers, image_url)
VALUES 
(
    'Đêm Nhạc Trịnh – Gọi Tên Bốn Mùa',
    'Một đêm nhạc lắng đọng với những bản tình ca bất hủ của nhạc sĩ Trịnh Công Sơn, tái hiện lại những cảm xúc xưa qua giọng ca các nghệ sĩ hàng đầu. Không gian gần gũi, mộc mạc nhưng đậm chất nghệ thuật, chắc chắn sẽ mang lại cho bạn một trải nghiệm khó quên.',
    '20:00 - 25/08/2025',
    'Nhà hát Hòa Bình',
    '240 Đường 3/2, Quận 10, TP.HCM',
    'Trang phục lịch sự.\nKhông mang đồ ăn, nước uống vào khán phòng.\nVé này không dành cho trẻ em dưới 8 tuổi.\nVui lòng không quay phim, chụp ảnh trong suốt chương trình.\nVé sẽ hết hiệu lực sau 15 phút kể từ thời điểm chương trình biểu diễn bắt đầu.',
    'Ban nhạc Mùa Thu, Ca sĩ Hồng Nhung, Ca sĩ Đức Tuấn',
    'Công ty Truyền Thông Mưa',
    'images/demnhactrinh.jpg'
),
(
    'Sân Khấu Hài – Tám Chuyện Cuối Tuần',
    'Một buổi biểu diễn hài kịch vui nhộn với sự tham gia của các nghệ sĩ hài nổi tiếng. Chương trình mang đến tiếng cười thư giãn sau một tuần làm việc căng thẳng. Nội dung phù hợp với mọi lứa tuổi và hứa hẹn sẽ là món quà tinh thần tuyệt vời cho bạn và gia đình.',
    '19:30 - 17/08/2025',
    'Nhà hát Kịch Sài Gòn',
    '30 Trần Hưng Đạo, Quận 1, TP.HCM',
    'Trang phục lịch sự.\nKhông mang đồ ăn, nước uống vào khán phòng.\nVui lòng không quay phim, chụp ảnh trong suốt chương trình.\nVé không hoàn tiền sau khi mua.\nVé sẽ hết hiệu lực sau 15 phút kể từ khi bắt đầu buổi diễn.',
    'Nhóm Hài Thứ Bảy, MC Đại Nghĩa',
    'Công ty Giải Trí Cười Vui',
    'images/haicuoi.jpg'
);



-- Thêm loại vé cho từng sự kiện
INSERT INTO ticket_type (name, price, event_id) VALUES
('Vé Thường', 250000, 1),
('Vé VIP', 500000, 1),
('Vé Standing', 300000, 2),
('Vé VIP', 650000, 2),
('Vé Thường', 200000, 3),
('Vé Premium', 400000, 3);

INSERT INTO user (username, email, password_hash) VALUES
('nguyenphuoc', 'nguyenphuoc@example.com', 'pbkdf2:sha256:260000$4CzGIE4U9tsdUb8U$ca5e306276e6d3ad60c4c2175b1575dd71dc4f11a6b7a33125a8e35dd8814fc3'),
('lethutrang', 'trang123@example.com', 'pbkdf2:sha256:260000$a1F2K5MvzUGtspFM$69b226d68c13be49d464d9f7fd735bfc0a35e3ed9c5a1e3c33c1cd9d4ec442a9'),
('phamvanan', 'anpham@example.com', 'pbkdf2:sha256:260000$8JGTQzGdrwLzYpJe$39f08a55808df07b3d8c6714e2cc786c2a3049e65cbb443c303d1850a2389dd5');

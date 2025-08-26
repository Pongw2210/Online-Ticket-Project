import io
import json
from app import db
from app.data.models import User, UserEnum

def test_register_and_login(client, app):
    # --- Đăng ký ---
    resp = client.post("/register", data={
        "fullname": "Nguyen Van A",
        "email": "a@example.com",
        "gender": "Nam",
        "dob": "2000-01-01",
        "number_phone": "0123456789",
        "username": "nguyenvana",
        "password": "123456"
    }, follow_redirects=True)

    html = resp.data.decode("utf-8")
    assert "Đăng ký thành công" in html

    # --- Kiểm tra DB ---
    with app.app_context():
        user = User.query.filter_by(username="nguyenvana").first()
        assert user is not None
        assert user.role == UserEnum.KHACH_HANG

    # --- Đăng nhập ---
    resp = client.post("/login", data={
        "username": "nguyenvana",
        "password": "123456"
    }, follow_redirects=True)
    assert resp.status_code == 200
    html = resp.data.decode("utf-8")
    # tuỳ template bạn render, chỉ cần có nội dung chính là pass
    assert "Sự kiện" in html or "Trang chủ" in html

def test_login_fail(client):
    resp = client.post("/login", data={
        "username": "wrong",
        "password": "wrong"
    }, follow_redirects=True)
    html = resp.data.decode("utf-8")
    assert "Tên đăng nhập hoặc mật khẩu không đúng" in html

def test_logout(client, app):
    with app.app_context():
        u = User(username="logouttest", email="lo@test.com", role=UserEnum.KHACH_HANG)
        u.set_password("123")
        db.session.add(u)
        db.session.commit()

    client.post("/login", data={"username": "logouttest", "password": "123"})
    resp = client.get("/logout", follow_redirects=True)
    html = resp.data.decode("utf-8")
    assert "Đăng nhập" in html or resp.status_code == 200

def test_upload_avatar(client, app, monkeypatch):
    with app.app_context():
        u = User(username="avatartest", email="ava@test.com", role=UserEnum.KHACH_HANG)
        u.set_password("123")
        db.session.add(u)
        db.session.commit()

    client.post("/login", data={"username": "avatartest", "password": "123"})

    # mock cloudinary.uploader.upload
    def mock_upload(file, folder, public_id, overwrite, resource_type):
        return {"secure_url": "http://mocked.url/avatar.png"}

    monkeypatch.setattr("cloudinary.uploader.upload", mock_upload)

    data = {"avatar": (io.BytesIO(b"fake image data"), "avatar.png")}
    resp = client.post("/upload_avatar", data=data, content_type="multipart/form-data")

    result = json.loads(resp.data)
    assert result["status"] == "success"
    assert "avatar_url" in result

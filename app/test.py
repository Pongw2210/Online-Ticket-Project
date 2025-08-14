from flask_mail import Message
from app import create_app, mail

app = create_app()

with app.app_context():
    msg = Message(
        subject="Test gửi mail",
        recipients=["2254052006bong@ou.edu.vn"],
        body="Hello từ Flask-Mail"
    )
    mail.send(msg)
    print("Mail đã gửi xong")
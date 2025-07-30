import hashlib
from app.data.models import User,EventTypeEnum

def get_user_by_id(user_id):
    return User.query.get(user_id)

def auth_user(username,password,role=None):
    hashed_password = hashlib.md5(password.encode('utf-8')).hexdigest()

    query = User.query.filter(
        User.username == username,
        User.password == hashed_password
    )

    if role:
        query = query.filter(User.role == role)

    return query.first()


def load_event_type_enum():
    return {
        etype.name: etype.value
        for etype in EventTypeEnum
    }

# from app import create_app
# app =create_app()
# if __name__ =="__main__":
#     with app.app_context():
#         # print(auth_user('userAdmin','123'))
#         load_event_type_enum()
class Config:
    SQLALCHEMY_DATABASE_URI = "sqlite:///events.db"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = "secret"
class Config:
    SQLALCHEMY_DATABASE_URI = "mysql+pymysql://root:Admin%40123@localhost:3306/ticket_db"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = "secret"

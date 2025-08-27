import os

class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY", "secret_key_test")
    SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_URL", "sqlite:///app.db")
    SQLALCHEMY_TRACK_MODIFICATIONS = False

import pytest
from app import create_app, db as _db
from app.config import Config
from sqlalchemy.orm import sessionmaker

class TestConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"
    WTF_CSRF_ENABLED = False

@pytest.fixture(scope="session")
def app():
    """Tạo Flask app cho testing"""
    app = create_app(TestConfig)
    with app.app_context():
        _db.create_all()
        yield app
        _db.drop_all()

@pytest.fixture(scope="session")
def client(app):
    """Client dùng để test các route"""
    return app.test_client()

@pytest.fixture(scope="function")
def db_session(app):
    """Tạo session riêng cho từng test và rollback sau test"""
    connection = _db.engine.connect()
    transaction = connection.begin()
    Session = sessionmaker(bind=connection)
    session = Session()

    yield session  # dùng session trực tiếp trong test

    session.close()
    transaction.rollback()
    connection.close()

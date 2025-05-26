# tests/conftest.py
import os, sys

# add the project root (where run.py and app/) to PYTHONPATH
ROOT = os.path.abspath(os.path.dirname(__file__) + os.sep + "..")
sys.path.insert(0, ROOT)


from app import create_app, db as _db
from flask_migrate import upgrade
import pytest

TEST_DB_URI = 'sqlite:///:memory:'

@pytest.fixture(scope='session')
def app():
    ###Create and configure a new app instance for each test session.
    os.environ['FLASK_ENV'] = 'testing'
    os.environ['DATABASE_URL'] = TEST_DB_URI
    app = create_app()
    app.config.update({
        'TESTING': True,
        'SQLALCHEMY_DATABASE_URI': TEST_DB_URI,
        'SQLALCHEMY_TRACK_MODIFICATIONS': False,
        'WTF_CSRF_ENABLED': False,
        'JWT_SECRET_KEY': 'test-secret'
    })
    with app.app_context():
        # If you want to run migrations instead of create_all():
        # upgrade()
        _db.create_all()
        yield app
        _db.drop_all()

@pytest.fixture
def client(app):
    """A test client for the app."""
    return app.test_client()

@pytest.fixture
def db(app):
    #"""Expose the database for direct model tests."""
    return _db

@pytest.fixture(autouse=True)
def clean_db(app, db):
    #"""Ensure a fresh schema before each test."""
    with app.app_context():
        db.drop_all()
        db.create_all()
    yield
    with app.app_context():
        db.session.remove()
        db.drop_all()

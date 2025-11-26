import pytest
from app.main import create_app
from app.models import db

@pytest.fixture(scope="session")
def app():
    app = create_app()
    with app.app_context():
        db.create_all()
    return app


@pytest.fixture
def client(app):
    return app.test_client()

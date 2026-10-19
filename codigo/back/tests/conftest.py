import os

import pytest

# Banco em memória para não apagar o moedas.db de desenvolvimento.
os.environ["DATABASE_URL"] = "sqlite:///:memory:"

from app import create_app  # noqa: E402
from app.extensions import db  # noqa: E402


@pytest.fixture
def client():
    app = create_app()
    app.config["TESTING"] = True

    with app.test_client() as client:
        yield client

    with app.app_context():
        db.drop_all()

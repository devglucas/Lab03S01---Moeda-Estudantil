import os

import pytest

# Banco em memória para não apagar o moedas.db de desenvolvimento.
os.environ["DATABASE_URL"] = "sqlite:///:memory:"
# Sem servidor de e-mail, mesmo que exista um .env local configurado.
for variavel in ("MAIL_HOST", "MAIL_USER", "MAIL_PASSWORD"):
    os.environ[variavel] = ""

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

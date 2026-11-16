import os
import tempfile

import pytest

# Banco em memória para não apagar o moedas.db de desenvolvimento.
os.environ["DATABASE_URL"] = "sqlite:///:memory:"
# Fotos das vantagens em uma pasta temporária, fora do repositório.
os.environ["UPLOAD_FOLDER"] = tempfile.mkdtemp(prefix="moedas-uploads-")
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


@pytest.fixture
def entrar(client):
    """Faz login e devolve o header de autorização para as rotas protegidas."""

    def _entrar(email, senha="senha123"):
        resp = client.post("/api/auth/login", json={"email": email, "senha": senha})
        assert resp.status_code == 200, resp.get_json()
        return {"Authorization": f"Bearer {resp.get_json()['token']}"}

    return _entrar

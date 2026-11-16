from datetime import datetime, timedelta, timezone

import jwt

ALUNO = {
    "nome": "Ana", "email": "ana@gmail.com", "cpf": "22222222222",
    "rg": "MG1", "endereco": "Rua A", "curso": "ES",
    "instituicaoId": 1, "senha": "senha123",
}
EMPRESA = {"nome": "Livraria", "email": "contato@livraria.com", "cnpj": "12345678000199", "senha": "senha123"}


def test_login_devolve_token_e_perfil(client):
    aluno = client.post("/api/alunos", json=ALUNO).get_json()

    resp = client.post("/api/auth/login", json={"email": "ANA@gmail.com ", "senha": "senha123"})

    assert resp.status_code == 200
    corpo = resp.get_json()
    assert corpo["token"]
    assert corpo["usuario"]["id"] == aluno["id"]
    assert corpo["usuario"]["tipo"] == "aluno"
    assert "senha_hash" not in corpo["usuario"]


def test_senha_errada_e_email_inexistente_tem_a_mesma_resposta(client):
    client.post("/api/alunos", json=ALUNO)

    errada = client.post("/api/auth/login", json={"email": "ana@gmail.com", "senha": "outra1"})
    inexistente = client.post("/api/auth/login", json={"email": "nao@existe.com", "senha": "senha123"})

    assert errada.status_code == inexistente.status_code == 401
    assert errada.get_json() == inexistente.get_json()


def test_login_sem_campos(client):
    resp = client.post("/api/auth/login", json={})

    assert resp.status_code == 400
    assert resp.get_json()["campos"].keys() == {"email", "senha"}
    assert client.post("/api/auth/login", json=[1]).status_code == 400


def test_eu_devolve_o_perfil_logado(client, entrar):
    client.post("/api/empresas", json=EMPRESA)

    resp = client.get("/api/auth/eu", headers=entrar("contato@livraria.com"))

    assert resp.status_code == 200
    assert resp.get_json()["tipo"] == "empresa"
    assert resp.get_json()["nome"] == "Livraria"


def test_rota_protegida_sem_token_ou_com_token_invalido(client):
    assert client.get("/api/auth/eu").status_code == 401
    assert client.get("/api/auth/eu", headers={"Authorization": "Bearer xyz"}).status_code == 401
    assert client.get("/api/auth/eu", headers={"Authorization": "xyz"}).status_code == 401


def test_token_expirado(client):
    aluno = client.post("/api/alunos", json=ALUNO).get_json()
    vencido = jwt.encode(
        {"sub": str(aluno["id"]), "exp": datetime.now(timezone.utc) - timedelta(minutes=1)},
        client.application.config["SECRET_KEY"],
        algorithm="HS256",
    )

    resp = client.get("/api/auth/eu", headers={"Authorization": f"Bearer {vencido}"})

    assert resp.status_code == 401


def test_token_de_usuario_removido(client, entrar):
    aluno = client.post("/api/alunos", json=ALUNO).get_json()
    cabecalho = entrar("ana@gmail.com")
    client.delete(f"/api/alunos/{aluno['id']}")

    assert client.get("/api/auth/eu", headers=cabecalho).status_code == 401

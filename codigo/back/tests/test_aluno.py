ALUNO = {
    "nome": "João",
    "email": "joao@gmail.com",
    "cpf": "123.456.789-01",
    "rg": "MG123456",
    "endereco": "Rua das Flores, 100",
    "curso": "Engenharia de Software",
    "instituicaoId": 1,
    "login": "joao123",
    "senha": "senha123",
}


def test_crud_completo(client):
    resp = client.post("/api/alunos", json=ALUNO)
    assert resp.status_code == 201
    aluno = resp.get_json()
    assert aluno["cpf"] == "12345678901"
    assert aluno["saldo"] == 0
    assert aluno["instituicaoNome"] == "PUC Minas"

    resp = client.get("/api/alunos")
    assert [a["nome"] for a in resp.get_json()] == ["João"]

    resp = client.get(f"/api/alunos/{aluno['id']}")
    assert resp.status_code == 200

    edicao = {**ALUNO, "nome": "João Franca", "curso": "Ciência da Computação"}
    del edicao["senha"]
    resp = client.put(f"/api/alunos/{aluno['id']}", json=edicao)
    assert resp.status_code == 200
    assert resp.get_json()["nome"] == "João Franca"

    resp = client.delete(f"/api/alunos/{aluno['id']}")
    assert resp.status_code == 204
    assert client.get(f"/api/alunos/{aluno['id']}").status_code == 404


def test_campos_obrigatorios(client):
    resp = client.post("/api/alunos", json={"nome": "Sem dados"})
    assert resp.status_code == 400
    campos = resp.get_json()["campos"]
    assert {"email", "cpf", "rg", "login", "senha", "instituicaoId"} <= campos.keys()


def test_instituicao_inexistente(client):
    resp = client.post("/api/alunos", json={**ALUNO, "instituicaoId": 999})
    assert resp.status_code == 400
    assert "instituicaoId" in resp.get_json()["campos"]


def test_cpf_duplicado(client):
    client.post("/api/alunos", json=ALUNO)
    resp = client.post(
        "/api/alunos",
        json={**ALUNO, "email": "outro@gmail.com", "login": "outro"},
    )
    assert resp.status_code == 409

ALUNO = {
    "nome": "Ana", "email": "ana@gmail.com", "cpf": "11122233344",
    "rg": "MG1", "endereco": "Rua A", "curso": "ES",
    "instituicaoId": 1, "senha": "senha123",
}


def test_lista_as_instituicoes_semeadas(client):
    resp = client.get("/api/instituicoes")
    assert [i["nome"] for i in resp.get_json()] == ["CEFET-MG", "PUC Minas", "UFMG"]


def test_crud_completo(client):
    resp = client.post("/api/instituicoes", json={"nome": "  UFOP  "})
    assert resp.status_code == 201
    instituicao = resp.get_json()
    assert instituicao["nome"] == "UFOP"

    resp = client.put(f"/api/instituicoes/{instituicao['id']}", json={"nome": "UFV"})
    assert resp.get_json()["nome"] == "UFV"

    resp = client.delete(f"/api/instituicoes/{instituicao['id']}")
    assert resp.status_code == 204
    assert client.get(f"/api/instituicoes/{instituicao['id']}").status_code == 404


def test_nome_duplicado(client):
    resp = client.post("/api/instituicoes", json={"nome": "UFMG"})
    assert resp.status_code == 409


def test_sem_json(client):
    resp = client.post("/api/instituicoes", data="texto")
    assert resp.status_code == 400
    assert resp.get_json()["campos"] == {"nome": "Envie os dados em JSON."}


def test_nao_remove_instituicao_com_alunos(client):
    client.post("/api/alunos", json=ALUNO)
    resp = client.delete("/api/instituicoes/1")
    assert resp.status_code == 409

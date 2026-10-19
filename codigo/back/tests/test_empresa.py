EMPRESA = {
    "nome": "Livraria Central",
    "email": "contato@livraria.com",
    "cnpj": "12.345.678/0001-90",
    "senha": "senha123",
}

ALUNO = {
    "nome": "Ana", "email": "ana@gmail.com", "cpf": "11122233344",
    "rg": "MG1", "endereco": "Rua A", "curso": "ES",
    "instituicaoId": 1, "senha": "senha123",
}


def test_crud_completo(client):
    resp = client.post("/api/empresas", json=EMPRESA)
    assert resp.status_code == 201
    empresa = resp.get_json()
    assert empresa["cnpj"] == "12345678000190"

    resp = client.get("/api/empresas")
    assert [e["nome"] for e in resp.get_json()] == ["Livraria Central"]

    edicao = {"nome": "Livraria Nova", "email": EMPRESA["email"], "cnpj": EMPRESA["cnpj"]}
    resp = client.put(f"/api/empresas/{empresa['id']}", json=edicao)
    assert resp.status_code == 200
    assert resp.get_json()["nome"] == "Livraria Nova"

    resp = client.delete(f"/api/empresas/{empresa['id']}")
    assert resp.status_code == 204
    assert client.get(f"/api/empresas/{empresa['id']}").status_code == 404


def test_cnpj_invalido(client):
    resp = client.post("/api/empresas", json={**EMPRESA, "cnpj": "123"})
    assert resp.status_code == 400
    assert "cnpj" in resp.get_json()["campos"]


def test_email_e_o_login_unico_entre_perfis(client):
    client.post("/api/empresas", json=EMPRESA)
    resp = client.post("/api/alunos", json={**ALUNO, "email": EMPRESA["email"]})
    assert resp.status_code == 409


def test_edicao_nao_aceita_email_de_outro_perfil(client):
    empresa = client.post("/api/empresas", json=EMPRESA).get_json()
    client.post("/api/alunos", json=ALUNO)

    edicao = {"nome": EMPRESA["nome"], "email": "ana@gmail.com", "cnpj": EMPRESA["cnpj"]}
    resp = client.put(f"/api/empresas/{empresa['id']}", json=edicao)
    assert resp.status_code == 409

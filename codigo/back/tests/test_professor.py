PROFESSOR = {
    "nome": "Carla", "email": "carla@puc.br", "cpf": "111.111.111-11",
    "departamento": "Computação", "instituicaoId": 1, "senha": "senha123",
}


def test_crud_completo(client):
    resp = client.post("/api/professores", json=PROFESSOR)
    assert resp.status_code == 201
    professor = resp.get_json()
    assert professor["cpf"] == "11111111111"
    assert professor["saldo"] == 1000

    edicao = {**PROFESSOR, "nome": "Carla Dias", "departamento": "Matemática"}
    del edicao["senha"]
    resp = client.put(f"/api/professores/{professor['id']}", json=edicao)
    assert resp.status_code == 200
    assert resp.get_json()["departamento"] == "Matemática"
    assert resp.get_json()["saldo"] == 1000

    resp = client.delete(f"/api/professores/{professor['id']}")
    assert resp.status_code == 204
    assert client.get(f"/api/professores/{professor['id']}").status_code == 404


def test_campos_obrigatorios(client):
    resp = client.post("/api/professores", json={"nome": "Sem dados"})
    assert resp.status_code == 400
    assert {"email", "cpf", "departamento", "senha", "instituicaoId"} <= resp.get_json()["campos"].keys()


def test_cpf_e_email_duplicados(client):
    client.post("/api/professores", json=PROFESSOR)
    assert client.post("/api/professores", json={**PROFESSOR, "email": "x@puc.br"}).status_code == 409
    assert client.post("/api/professores", json={**PROFESSOR, "cpf": "22222222222"}).status_code == 409

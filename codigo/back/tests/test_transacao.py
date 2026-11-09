from sqlalchemy import event
from sqlalchemy.exc import IntegrityError

from app.extensions import db
from app.models.transacao import EnvioMoeda, TrocaVantagem

PROFESSOR = {
    "nome": "Carla", "email": "carla@puc.br", "cpf": "11111111111",
    "departamento": "Computação", "instituicaoId": 1, "senha": "senha123",
}
ALUNO = {
    "nome": "Ana", "email": "ana@gmail.com", "cpf": "22222222222",
    "rg": "MG1", "endereco": "Rua A", "curso": "ES",
    "instituicaoId": 1, "senha": "senha123",
}


def _cenario(client):
    professor = client.post("/api/professores", json=PROFESSOR).get_json()
    aluno = client.post("/api/alunos", json=ALUNO).get_json()
    envio = {
        "professorId": professor["id"],
        "alunoId": aluno["id"],
        "valor": 100,
        "mensagem": "Ótima participação",
    }
    return professor, aluno, envio


def _saldos(client, professor, aluno):
    return (
        client.get(f"/api/professores/{professor['id']}").get_json()["saldo"],
        client.get(f"/api/alunos/{aluno['id']}").get_json()["saldo"],
    )


def test_envio_debita_credita_e_registra(client):
    professor, aluno, envio = _cenario(client)

    resp = client.post("/api/transacoes", json=envio)

    assert resp.status_code == 201
    corpo = resp.get_json()
    assert corpo["tipo"] == "envio"
    assert corpo["mensagem"] == "Ótima participação"
    assert corpo["data"].endswith("+00:00")
    assert _saldos(client, professor, aluno) == (900, 100)


def test_saldo_insuficiente_nao_altera_nada(client):
    professor, aluno, envio = _cenario(client)

    resp = client.post("/api/transacoes", json={**envio, "valor": 1001})

    assert resp.status_code == 400
    assert "Saldo insuficiente" in resp.get_json()["erro"]
    assert "valor" in resp.get_json()["campos"]
    assert _saldos(client, professor, aluno) == (1000, 0)
    assert client.get("/api/transacoes").get_json() == []


def test_pode_enviar_exatamente_o_saldo(client):
    professor, aluno, envio = _cenario(client)

    resp = client.post("/api/transacoes", json={**envio, "valor": 1000})

    assert resp.status_code == 201
    assert _saldos(client, professor, aluno) == (0, 1000)


def test_falha_na_gravacao_desfaz_debito_e_credito(client):
    professor, aluno, envio = _cenario(client)

    def falhar(*_):
        raise IntegrityError("insert", {}, Exception("falha simulada"))

    event.listen(EnvioMoeda, "before_insert", falhar)
    try:
        resp = client.post("/api/transacoes", json=envio)
    finally:
        event.remove(EnvioMoeda, "before_insert", falhar)

    assert resp.status_code == 409
    assert _saldos(client, professor, aluno) == (1000, 0)
    assert client.get("/api/transacoes").get_json() == []


def test_campos_invalidos(client):
    resp = client.post("/api/transacoes", json={"valor": 0, "mensagem": 123})

    assert resp.status_code == 400
    assert resp.get_json()["campos"].keys() == {
        "professorId", "alunoId", "valor", "mensagem",
    }


def test_valor_nao_inteiro_e_rejeitado(client):
    _, _, envio = _cenario(client)
    for valor in (1.5, "10", True, -1):
        resp = client.post("/api/transacoes", json={**envio, "valor": valor})
        assert resp.status_code == 400, valor


def test_corpo_que_nao_e_objeto_json(client):
    assert client.post("/api/transacoes", json=[1]).status_code == 400
    assert client.post("/api/transacoes", data="texto").status_code == 400


def test_professor_ou_aluno_inexistente(client):
    _, _, envio = _cenario(client)
    assert client.post("/api/transacoes", json={**envio, "professorId": 999}).status_code == 404
    assert client.post("/api/transacoes", json={**envio, "alunoId": 999}).status_code == 404


def test_aluno_de_outra_instituicao(client):
    professor, _, envio = _cenario(client)
    outro = client.post(
        "/api/alunos",
        json={**ALUNO, "email": "bia@gmail.com", "cpf": "33333333333", "instituicaoId": 2},
    ).get_json()

    resp = client.post("/api/transacoes", json={**envio, "alunoId": outro["id"]})

    assert resp.status_code == 400
    assert "alunoId" in resp.get_json()["campos"]
    assert client.get(f"/api/professores/{professor['id']}").get_json()["saldo"] == 1000


def test_extrato_do_professor_lista_os_envios_dele(client):
    professor, aluno, envio = _cenario(client)
    colega = client.post(
        "/api/professores",
        json={**PROFESSOR, "email": "rui@puc.br", "cpf": "44444444444"},
    ).get_json()
    client.post("/api/transacoes", json=envio)
    client.post("/api/transacoes", json={**envio, "valor": 50})
    client.post("/api/transacoes", json={**envio, "professorId": colega["id"], "valor": 7})

    extrato = client.get(f"/api/transacoes/extrato/professor/{professor['id']}").get_json()

    assert extrato["saldo"] == 850
    assert [t["valor"] for t in extrato["transacoes"]] == [50, 100]


def test_extrato_do_aluno_traz_envios_e_trocas(client):
    _, aluno, envio = _cenario(client)
    client.post("/api/transacoes", json=envio)

    with client.application.app_context():
        db.session.add(TrocaVantagem(aluno_id=aluno["id"], valor=30, codigo="CUPOM1"))
        db.session.commit()

    extrato = client.get(f"/api/transacoes/extrato/aluno/{aluno['id']}").get_json()

    assert {t["tipo"] for t in extrato["transacoes"]} == {"envio", "troca"}
    troca = next(t for t in extrato["transacoes"] if t["tipo"] == "troca")
    assert troca["codigo"] == "CUPOM1"


def test_extrato_de_usuario_inexistente(client):
    assert client.get("/api/transacoes/extrato/professor/999").status_code == 404
    assert client.get("/api/transacoes/extrato/aluno/999").status_code == 404


def test_nao_remove_quem_tem_transacoes(client):
    professor, aluno, envio = _cenario(client)
    client.post("/api/transacoes", json=envio)

    assert client.delete(f"/api/alunos/{aluno['id']}").status_code == 409
    assert client.delete(f"/api/professores/{professor['id']}").status_code == 409
    assert client.get("/api/transacoes").status_code == 200
    assert client.get(f"/api/transacoes/extrato/professor/{professor['id']}").status_code == 200

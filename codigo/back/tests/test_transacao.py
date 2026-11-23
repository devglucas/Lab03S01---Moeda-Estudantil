from sqlalchemy import event
from sqlalchemy.exc import IntegrityError

from app.extensions import db
from app.models.empresa import EmpresaParceira
from app.models.transacao import EnvioMoeda, TrocaVantagem
from app.models.vantagem import Vantagem

PROFESSOR = {
    "nome": "Carla", "email": "carla@puc.br", "cpf": "11111111111",
    "departamento": "Computação", "instituicaoId": 1, "senha": "senha123",
}
ALUNO = {
    "nome": "Ana", "email": "ana@gmail.com", "cpf": "22222222222",
    "rg": "MG1", "endereco": "Rua A", "curso": "ES",
    "instituicaoId": 1, "senha": "senha123",
}


def _cenario(client, entrar):
    """Cadastra professor e aluno; devolve os dois, o envio e o login do professor."""
    professor = client.post("/api/professores", json=PROFESSOR).get_json()
    aluno = client.post("/api/alunos", json=ALUNO).get_json()
    envio = {"alunoId": aluno["id"], "valor": 100, "mensagem": "Ótima participação"}
    return professor, aluno, envio, entrar(PROFESSOR["email"])


def _saldos(client, professor, aluno):
    return (
        client.get(f"/api/professores/{professor['id']}").get_json()["saldo"],
        client.get(f"/api/alunos/{aluno['id']}").get_json()["saldo"],
    )


def _extrato(client, cabecalho):
    return client.get("/api/transacoes/extrato", headers=cabecalho).get_json()


def test_envio_debita_credita_e_registra(client, entrar):
    professor, aluno, envio, cabecalho = _cenario(client, entrar)

    resp = client.post("/api/transacoes", json=envio, headers=cabecalho)

    assert resp.status_code == 201
    corpo = resp.get_json()
    assert corpo["tipo"] == "envio"
    assert corpo["professorId"] == professor["id"]
    assert corpo["mensagem"] == "Ótima participação"
    assert corpo["data"].endswith("+00:00")
    assert _saldos(client, professor, aluno) == (900, 100)


def test_o_professor_e_sempre_o_usuario_logado(client, entrar):
    professor, aluno, envio, cabecalho = _cenario(client, entrar)
    colega = client.post(
        "/api/professores",
        json={**PROFESSOR, "email": "rui@puc.br", "cpf": "44444444444"},
    ).get_json()

    resp = client.post(
        "/api/transacoes", json={**envio, "professorId": colega["id"]}, headers=cabecalho
    )

    assert resp.get_json()["professorId"] == professor["id"]
    assert client.get(f"/api/professores/{colega['id']}").get_json()["saldo"] == 1000


def test_envio_exige_login_de_professor(client, entrar):
    _, _, envio, _ = _cenario(client, entrar)

    assert client.post("/api/transacoes", json=envio).status_code == 401
    resp = client.post("/api/transacoes", json=envio, headers=entrar(ALUNO["email"]))
    assert resp.status_code == 403


def test_saldo_insuficiente_nao_altera_nada(client, entrar):
    professor, aluno, envio, cabecalho = _cenario(client, entrar)

    resp = client.post("/api/transacoes", json={**envio, "valor": 1001}, headers=cabecalho)

    assert resp.status_code == 400
    assert "Saldo insuficiente" in resp.get_json()["erro"]
    assert "valor" in resp.get_json()["campos"]
    assert _saldos(client, professor, aluno) == (1000, 0)
    assert _extrato(client, cabecalho)["transacoes"] == []


def test_pode_enviar_exatamente_o_saldo(client, entrar):
    professor, aluno, envio, cabecalho = _cenario(client, entrar)

    resp = client.post("/api/transacoes", json={**envio, "valor": 1000}, headers=cabecalho)

    assert resp.status_code == 201
    assert _saldos(client, professor, aluno) == (0, 1000)


def test_falha_na_gravacao_desfaz_debito_e_credito(client, entrar):
    professor, aluno, envio, cabecalho = _cenario(client, entrar)

    def falhar(*_):
        raise IntegrityError("insert", {}, Exception("falha simulada"))

    event.listen(EnvioMoeda, "before_insert", falhar)
    try:
        resp = client.post("/api/transacoes", json=envio, headers=cabecalho)
    finally:
        event.remove(EnvioMoeda, "before_insert", falhar)

    assert resp.status_code == 409
    assert _saldos(client, professor, aluno) == (1000, 0)
    assert _extrato(client, cabecalho)["transacoes"] == []


def test_campos_invalidos(client, entrar):
    _, _, _, cabecalho = _cenario(client, entrar)

    resp = client.post(
        "/api/transacoes", json={"valor": 0, "mensagem": 123}, headers=cabecalho
    )

    assert resp.status_code == 400
    assert resp.get_json()["campos"].keys() == {"alunoId", "valor", "mensagem"}


def test_valor_nao_inteiro_e_rejeitado(client, entrar):
    _, _, envio, cabecalho = _cenario(client, entrar)
    for valor in (1.5, "10", True, -1):
        resp = client.post("/api/transacoes", json={**envio, "valor": valor}, headers=cabecalho)
        assert resp.status_code == 400, valor


def test_corpo_que_nao_e_objeto_json(client, entrar):
    _, _, _, cabecalho = _cenario(client, entrar)

    assert client.post("/api/transacoes", json=[1], headers=cabecalho).status_code == 400
    assert client.post("/api/transacoes", data="texto", headers=cabecalho).status_code == 400


def test_aluno_inexistente(client, entrar):
    _, _, envio, cabecalho = _cenario(client, entrar)

    resp = client.post("/api/transacoes", json={**envio, "alunoId": 999}, headers=cabecalho)

    assert resp.status_code == 404


def test_aluno_de_outra_instituicao(client, entrar):
    professor, _, envio, cabecalho = _cenario(client, entrar)
    outro = client.post(
        "/api/alunos",
        json={**ALUNO, "email": "bia@gmail.com", "cpf": "33333333333", "instituicaoId": 2},
    ).get_json()

    resp = client.post(
        "/api/transacoes", json={**envio, "alunoId": outro["id"]}, headers=cabecalho
    )

    assert resp.status_code == 400
    assert "alunoId" in resp.get_json()["campos"]
    assert client.get(f"/api/professores/{professor['id']}").get_json()["saldo"] == 1000


def test_extrato_do_professor_lista_so_os_envios_dele(client, entrar):
    _, _, envio, cabecalho = _cenario(client, entrar)
    client.post(
        "/api/professores",
        json={**PROFESSOR, "email": "rui@puc.br", "cpf": "44444444444"},
    )
    client.post("/api/transacoes", json=envio, headers=cabecalho)
    client.post("/api/transacoes", json={**envio, "valor": 50}, headers=cabecalho)
    client.post("/api/transacoes", json={**envio, "valor": 7}, headers=entrar("rui@puc.br"))

    extrato = _extrato(client, cabecalho)

    assert extrato["saldo"] == 850
    assert [t["valor"] for t in extrato["transacoes"]] == [50, 100]


def test_extrato_do_aluno_traz_envios_e_trocas(client, entrar):
    _, aluno, envio, cabecalho = _cenario(client, entrar)
    client.post("/api/transacoes", json=envio, headers=cabecalho)

    with client.application.app_context():
        empresa = EmpresaParceira(
            login="loja@x.com", senha_hash="-", nome="Loja", email="loja@x.com", cnpj="12345678000199"
        )
        vantagem = Vantagem(nome="Caneca", descricao="Caneca da loja", custo=30, empresa=empresa)
        db.session.add(TrocaVantagem(aluno_id=aluno["id"], valor=30, codigo="CUPOM1", vantagem=vantagem))
        db.session.commit()

    extrato = _extrato(client, entrar(ALUNO["email"]))

    assert extrato["saldo"] == 100
    assert {t["tipo"] for t in extrato["transacoes"]} == {"envio", "troca"}
    troca = next(t for t in extrato["transacoes"] if t["tipo"] == "troca")
    assert troca["codigo"] == "CUPOM1"
    assert troca["vantagemNome"] == "Caneca"
    assert troca["empresaNome"] == "Loja"


def test_extrato_exige_login_de_aluno_ou_professor(client, entrar):
    client.post(
        "/api/empresas",
        json={"nome": "Loja", "email": "loja@x.com", "cnpj": "12345678000199", "senha": "senha123"},
    )

    assert client.get("/api/transacoes/extrato").status_code == 401
    assert client.get("/api/transacoes/extrato", headers=entrar("loja@x.com")).status_code == 403


def test_nao_remove_quem_tem_transacoes(client, entrar):
    professor, aluno, envio, cabecalho = _cenario(client, entrar)
    client.post("/api/transacoes", json=envio, headers=cabecalho)

    assert client.delete(f"/api/alunos/{aluno['id']}").status_code == 409
    assert client.delete(f"/api/professores/{professor['id']}").status_code == 409
    assert client.get("/api/transacoes/extrato", headers=cabecalho).status_code == 200

import re
from unittest import mock

import pytest
from sqlalchemy import event
from sqlalchemy.exc import IntegrityError

from app.models.transacao import TrocaVantagem

PROFESSOR = {
    "nome": "Carla", "email": "carla@puc.br", "cpf": "11111111111",
    "departamento": "Computação", "instituicaoId": 1, "senha": "senha123",
}
ALUNO = {
    "nome": "Ana", "email": "ana@gmail.com", "cpf": "22222222222",
    "rg": "MG1", "endereco": "Rua A", "curso": "ES",
    "instituicaoId": 1, "senha": "senha123",
}
EMPRESA = {"nome": "Livraria", "email": "contato@livraria.com", "cnpj": "12345678000199", "senha": "senha123"}
OUTRA_EMPRESA = {"nome": "Cantina", "email": "cantina@x.com", "cnpj": "98765432000155", "senha": "senha123"}


@pytest.fixture
def cenario(client, entrar):
    """Aluno com 300 moedas e duas vantagens da Livraria: uma de 100 e outra de 500."""
    client.post("/api/professores", json=PROFESSOR)
    aluno = client.post("/api/alunos", json=ALUNO).get_json()
    client.post("/api/empresas", json=EMPRESA)
    client.post(
        "/api/transacoes",
        json={"alunoId": aluno["id"], "valor": 300, "mensagem": "Monitoria"},
        headers=entrar(PROFESSOR["email"]),
    )

    empresa = entrar(EMPRESA["email"])
    livro = _vantagem(client, empresa, "Livro", 100)
    curso = _vantagem(client, empresa, "Curso", 500)
    return {"aluno": entrar(ALUNO["email"]), "empresa": empresa, "livro": livro, "curso": curso}


def _vantagem(client, cabecalho, nome, custo):
    return client.post(
        "/api/vantagens",
        data={"nome": nome, "descricao": f"{nome} da loja", "custo": str(custo)},
        headers=cabecalho,
        content_type="multipart/form-data",
    ).get_json()


def _trocar(client, cabecalho, vantagem):
    return client.post("/api/trocas", json={"vantagemId": vantagem["id"]}, headers=cabecalho)


def _saldo(client, cabecalho):
    return client.get("/api/auth/eu", headers=cabecalho).get_json()["saldo"]


def test_troca_debita_o_saldo_e_gera_o_cupom(client, cenario):
    resp = _trocar(client, cenario["aluno"], cenario["livro"])

    assert resp.status_code == 201
    troca = resp.get_json()
    assert troca["tipo"] == "troca"
    assert troca["valor"] == 100
    assert troca["vantagemNome"] == "Livro"
    assert troca["empresaNome"] == "Livraria"
    assert re.fullmatch(r"[A-Z2-9]{4}-[A-Z2-9]{4}", troca["codigo"])
    assert _saldo(client, cenario["aluno"]) == 200


def test_troca_aparece_no_extrato_do_aluno(client, cenario):
    _trocar(client, cenario["aluno"], cenario["livro"])

    extrato = client.get("/api/transacoes/extrato", headers=cenario["aluno"]).get_json()

    assert extrato["saldo"] == 200
    assert [(t["tipo"], t["valor"]) for t in extrato["transacoes"]] == [("troca", 100), ("envio", 300)]


def test_saldo_insuficiente_nao_altera_nada(client, cenario):
    resp = _trocar(client, cenario["aluno"], cenario["curso"])

    assert resp.status_code == 400
    assert "Saldo insuficiente" in resp.get_json()["erro"]
    assert _saldo(client, cenario["aluno"]) == 300
    assert client.get("/api/trocas", headers=cenario["empresa"]).get_json() == []


def test_pode_trocar_exatamente_o_saldo(client, cenario):
    tres = _vantagem(client, cenario["empresa"], "Kit", 300)

    assert _trocar(client, cenario["aluno"], tres).status_code == 201
    assert _saldo(client, cenario["aluno"]) == 0


def test_codigos_sao_unicos(client, cenario):
    primeira = _trocar(client, cenario["aluno"], cenario["livro"]).get_json()
    segunda = _trocar(client, cenario["aluno"], cenario["livro"]).get_json()

    assert primeira["codigo"] != segunda["codigo"]


def test_gera_outro_codigo_quando_o_sorteado_ja_existe(client, cenario):
    primeira = _trocar(client, cenario["aluno"], cenario["livro"]).get_json()
    sorteios = iter(primeira["codigo"].replace("-", "") + "ABCD2345")

    with mock.patch("app.services.troca_service.secrets.choice", side_effect=lambda _: next(sorteios)):
        segunda = _trocar(client, cenario["aluno"], cenario["livro"]).get_json()

    assert segunda["codigo"] == "ABCD-2345"


def test_falha_na_gravacao_desfaz_o_debito(client, cenario):
    def falhar(*_):
        raise IntegrityError("insert", {}, Exception("falha simulada"))

    event.listen(TrocaVantagem, "before_insert", falhar)
    try:
        resp = _trocar(client, cenario["aluno"], cenario["livro"])
    finally:
        event.remove(TrocaVantagem, "before_insert", falhar)

    assert resp.status_code == 409
    assert _saldo(client, cenario["aluno"]) == 300


@pytest.mark.parametrize("corpo", [{}, {"vantagemId": "1"}, {"vantagemId": 0}, {"vantagemId": True}])
def test_vantagem_invalida(client, cenario, corpo):
    resp = client.post("/api/trocas", json=corpo, headers=cenario["aluno"])

    assert resp.status_code == 400
    assert "vantagemId" in resp.get_json()["campos"]


def test_vantagem_inexistente(client, cenario):
    assert _trocar(client, cenario["aluno"], {"id": 999}).status_code == 404


def test_troca_exige_login_de_aluno(client, cenario):
    assert _trocar(client, {}, cenario["livro"]).status_code == 401
    assert _trocar(client, cenario["empresa"], cenario["livro"]).status_code == 403


def test_aluno_e_empresa_recebem_o_mesmo_codigo_por_email(client, cenario):
    client.application.config.update(MAIL_HOST="smtp.teste", MAIL_USER="", MAIL_USE_TLS=False)

    with mock.patch("smtplib.SMTP") as smtp:
        troca = _trocar(client, cenario["aluno"], cenario["livro"]).get_json()

    conexao = smtp.return_value.__enter__.return_value
    mensagens = {c.args[0]["To"]: c.args[0] for c in conexao.send_message.call_args_list}
    assert mensagens.keys() == {"ana@gmail.com", "contato@livraria.com"}

    cupom = mensagens["ana@gmail.com"]
    assert cupom["Subject"] == "Seu cupom: Livro"
    assert f"Código do cupom: {troca['codigo']}" in cupom.get_content()
    assert "saldo atual é de 200" in cupom.get_content()

    conferencia = mensagens["contato@livraria.com"]
    assert conferencia["Subject"] == "Nova troca de vantagem"
    assert f"Código do cupom: {troca['codigo']}" in conferencia.get_content()
    assert "Aluno: Ana" in conferencia.get_content()


def test_saldo_insuficiente_nao_envia_email(client, cenario):
    client.application.config.update(MAIL_HOST="smtp.teste")

    with mock.patch("smtplib.SMTP") as smtp:
        _trocar(client, cenario["aluno"], cenario["curso"])

    smtp.assert_not_called()


def test_empresa_confere_so_as_trocas_das_proprias_vantagens(client, entrar, cenario):
    client.post("/api/empresas", json=OUTRA_EMPRESA)
    outra = entrar(OUTRA_EMPRESA["email"])
    lanche = _vantagem(client, outra, "Lanche", 20)
    troca = _trocar(client, cenario["aluno"], cenario["livro"]).get_json()
    _trocar(client, cenario["aluno"], lanche)

    trocas = client.get("/api/trocas", headers=cenario["empresa"]).get_json()

    assert [(t["codigo"], t["alunoNome"], t["vantagemNome"]) for t in trocas] == [
        (troca["codigo"], "Ana", "Livro")
    ]
    assert client.get("/api/trocas", headers=cenario["aluno"]).status_code == 403


def test_vantagem_trocada_nao_pode_ser_removida(client, cenario):
    _trocar(client, cenario["aluno"], cenario["livro"])

    resp = client.delete(f"/api/vantagens/{cenario['livro']['id']}", headers=cenario["empresa"])

    assert resp.status_code == 409
    assert len(client.get("/api/vantagens/minhas", headers=cenario["empresa"]).get_json()) == 2


def test_troca_guarda_o_custo_da_epoca(client, cenario):
    troca = _trocar(client, cenario["aluno"], cenario["livro"]).get_json()
    client.put(
        f"/api/vantagens/{cenario['livro']['id']}",
        data={"nome": "Livro", "descricao": "Livro da loja", "custo": "150"},
        headers=cenario["empresa"],
        content_type="multipart/form-data",
    )

    trocas = client.get("/api/trocas", headers=cenario["empresa"]).get_json()

    assert trocas[0]["codigo"] == troca["codigo"]
    assert trocas[0]["valor"] == 100


def test_nao_remove_aluno_que_ja_trocou(client, cenario):
    _trocar(client, cenario["aluno"], cenario["livro"])
    aluno_id = client.get("/api/auth/eu", headers=cenario["aluno"]).get_json()["id"]

    assert client.delete(f"/api/alunos/{aluno_id}").status_code == 409

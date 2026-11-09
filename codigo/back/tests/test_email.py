from unittest import mock

from sqlalchemy import event
from sqlalchemy.exc import IntegrityError

from app.models.transacao import EnvioMoeda

PROFESSOR = {
    "nome": "Carla", "email": "carla@puc.br", "cpf": "11111111111",
    "departamento": "Computação", "instituicaoId": 1, "senha": "senha123",
}
ALUNO = {
    "nome": "Ana", "email": "ana@gmail.com", "cpf": "22222222222",
    "rg": "MG1", "endereco": "Rua A", "curso": "ES",
    "instituicaoId": 1, "senha": "senha123",
}


def _envio(client):
    professor = client.post("/api/professores", json=PROFESSOR).get_json()
    aluno = client.post("/api/alunos", json=ALUNO).get_json()
    return {
        "professorId": professor["id"],
        "alunoId": aluno["id"],
        "valor": 100,
        "mensagem": "Ótima participação",
    }


def _configurar_smtp(client):
    client.application.config.update(
        MAIL_HOST="smtp.teste", MAIL_USER="usuario", MAIL_PASSWORD="segredo"
    )


def _mensagens(smtp):
    conexao = smtp.return_value.__enter__.return_value
    return {
        chamada.args[0]["To"]: chamada.args[0]
        for chamada in conexao.send_message.call_args_list
    }


def test_professor_e_aluno_recebem_templates_diferentes(client):
    envio = _envio(client)
    _configurar_smtp(client)

    with mock.patch("smtplib.SMTP") as smtp:
        resp = client.post("/api/transacoes", json=envio)

    assert resp.status_code == 201
    mensagens = _mensagens(smtp)
    assert mensagens.keys() == {"carla@puc.br", "ana@gmail.com"}

    professor = mensagens["carla@puc.br"]
    assert professor["Subject"] == "Envio de moedas confirmado"
    corpo = professor.get_content()
    assert "Confirmamos que o seu envio" in corpo
    assert "Aluno: Ana" in corpo
    assert "saldo atual é de 900" in corpo

    aluno = mensagens["ana@gmail.com"]
    assert aluno["Subject"] == "Você recebeu moedas!"
    corpo = aluno.get_content()
    assert "Você recebeu moedas" in corpo
    assert "Professor: Carla" in corpo
    assert "Ótima participação" in corpo
    assert "saldo atual é de 100" in corpo


def test_usa_as_credenciais_e_o_timeout_configurados(client):
    envio = _envio(client)
    _configurar_smtp(client)

    with mock.patch("smtplib.SMTP") as smtp:
        client.post("/api/transacoes", json=envio)

    smtp.assert_called_with("smtp.teste", 587, timeout=10)
    conexao = smtp.return_value.__enter__.return_value
    conexao.starttls.assert_called()
    conexao.login.assert_called_with("usuario", "segredo")


def test_falha_no_email_nao_desfaz_o_envio(client):
    envio = _envio(client)
    _configurar_smtp(client)

    with mock.patch("smtplib.SMTP", side_effect=OSError("sem conexão")):
        resp = client.post("/api/transacoes", json=envio)

    assert resp.status_code == 201
    assert client.get(f"/api/alunos/{envio['alunoId']}").get_json()["saldo"] == 100


def test_saldo_insuficiente_nao_envia_email(client):
    envio = _envio(client)
    _configurar_smtp(client)

    with mock.patch("smtplib.SMTP") as smtp:
        client.post("/api/transacoes", json={**envio, "valor": 5000})

    smtp.assert_not_called()


def test_falha_na_gravacao_nao_envia_email(client):
    envio = _envio(client)
    _configurar_smtp(client)

    def falhar(*_):
        raise IntegrityError("insert", {}, Exception("falha simulada"))

    event.listen(EnvioMoeda, "before_insert", falhar)
    try:
        with mock.patch("smtplib.SMTP") as smtp:
            resp = client.post("/api/transacoes", json=envio)
    finally:
        event.remove(EnvioMoeda, "before_insert", falhar)

    assert resp.status_code == 409
    smtp.assert_not_called()


def test_sem_servidor_configurado_nao_abre_conexao(client):
    envio = _envio(client)

    with mock.patch("smtplib.SMTP") as smtp:
        resp = client.post("/api/transacoes", json=envio)

    assert resp.status_code == 201
    smtp.assert_not_called()

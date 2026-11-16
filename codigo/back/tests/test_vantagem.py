import io
import os

import pytest

EMPRESA = {"nome": "Livraria", "email": "contato@livraria.com", "cnpj": "12345678000199", "senha": "senha123"}
OUTRA_EMPRESA = {"nome": "Cantina", "email": "cantina@x.com", "cnpj": "98765432000155", "senha": "senha123"}
ALUNO = {
    "nome": "Ana", "email": "ana@gmail.com", "cpf": "22222222222",
    "rg": "MG1", "endereco": "Rua A", "curso": "ES",
    "instituicaoId": 1, "senha": "senha123",
}
VANTAGEM = {"nome": "Desconto de 10%", "descricao": "Em qualquer livro da loja", "custo": "50"}


@pytest.fixture
def empresa(client, entrar):
    """Login da empresa parceira já cadastrada."""
    client.post("/api/empresas", json=EMPRESA)
    return entrar(EMPRESA["email"])


def _foto(nome="foto.png"):
    return (io.BytesIO(b"conteudo da imagem"), nome)


def _cadastrar(client, cabecalho, **dados):
    return client.post(
        "/api/vantagens",
        data={**VANTAGEM, **dados},
        headers=cabecalho,
        content_type="multipart/form-data",
    )


def _caminho_da_foto(client, nome):
    return os.path.join(client.application.config["UPLOAD_FOLDER"], nome)


def test_cadastra_com_foto_e_serve_a_imagem(client, empresa):
    resp = _cadastrar(client, empresa, foto=_foto())

    assert resp.status_code == 201
    corpo = resp.get_json()
    assert corpo["nome"] == "Desconto de 10%"
    assert corpo["custo"] == 50
    assert corpo["empresaNome"] == "Livraria"
    assert corpo["foto"].endswith(".png")
    assert client.get(f"/uploads/{corpo['foto']}").data == b"conteudo da imagem"


def test_foto_e_opcional(client, empresa):
    resp = _cadastrar(client, empresa)

    assert resp.status_code == 201
    assert resp.get_json()["foto"] is None


def test_a_empresa_e_sempre_a_logada(client, empresa):
    outra = client.post("/api/empresas", json=OUTRA_EMPRESA).get_json()

    resp = _cadastrar(client, empresa, empresaId=str(outra["id"]))

    assert resp.get_json()["empresaNome"] == "Livraria"


def test_campos_obrigatorios(client, empresa):
    resp = client.post(
        "/api/vantagens", data={}, headers=empresa, content_type="multipart/form-data"
    )

    assert resp.status_code == 400
    assert resp.get_json()["campos"].keys() == {"nome", "descricao", "custo"}


@pytest.mark.parametrize("custo", ["abc", "-5", "0", "1.5", " "])
def test_custo_precisa_ser_inteiro_positivo(client, empresa, custo):
    resp = _cadastrar(client, empresa, custo=custo)

    assert resp.status_code == 400
    assert "custo" in resp.get_json()["campos"]


def test_textos_longos_demais(client, empresa):
    resp = _cadastrar(client, empresa, nome="x" * 121, descricao="y" * 501)

    assert resp.status_code == 400
    assert resp.get_json()["campos"].keys() == {"nome", "descricao"}


def test_formato_de_foto_invalido_nao_grava_nada(client, empresa):
    resp = _cadastrar(client, empresa, foto=_foto("animacao.gif"))

    assert resp.status_code == 400
    assert "foto" in resp.get_json()["campos"]
    assert client.get("/api/vantagens/minhas", headers=empresa).get_json() == []


def test_foto_grande_demais(client, empresa):
    grande = (io.BytesIO(b"0" * (5 * 1024 * 1024 + 1)), "foto.png")

    resp = _cadastrar(client, empresa, foto=grande)

    assert resp.status_code == 413
    assert "foto" in resp.get_json()["campos"]


def test_cadastro_exige_login_de_empresa(client, entrar):
    client.post("/api/alunos", json=ALUNO)

    assert _cadastrar(client, {}).status_code == 401
    assert _cadastrar(client, entrar(ALUNO["email"])).status_code == 403


def test_empresa_lista_so_as_proprias_vantagens(client, entrar, empresa):
    client.post("/api/empresas", json=OUTRA_EMPRESA)
    _cadastrar(client, empresa, nome="Primeira")
    _cadastrar(client, empresa, nome="Segunda")
    _cadastrar(client, entrar(OUTRA_EMPRESA["email"]), nome="Da cantina")

    minhas = client.get("/api/vantagens/minhas", headers=empresa).get_json()

    assert [v["nome"] for v in minhas] == ["Segunda", "Primeira"]


def test_edita_mantendo_a_foto_quando_nao_vem_outra(client, empresa):
    criada = _cadastrar(client, empresa, foto=_foto()).get_json()

    resp = client.put(
        f"/api/vantagens/{criada['id']}",
        data={**VANTAGEM, "custo": "80"},
        headers=empresa,
        content_type="multipart/form-data",
    )

    assert resp.status_code == 200
    assert resp.get_json()["custo"] == 80
    assert resp.get_json()["foto"] == criada["foto"]


def test_trocar_a_foto_apaga_a_antiga(client, empresa):
    criada = _cadastrar(client, empresa, foto=_foto()).get_json()

    resp = client.put(
        f"/api/vantagens/{criada['id']}",
        data={**VANTAGEM, "foto": _foto("nova.jpg")},
        headers=empresa,
        content_type="multipart/form-data",
    )

    nova = resp.get_json()["foto"]
    assert nova.endswith(".jpg")
    assert os.path.exists(_caminho_da_foto(client, nova))
    assert not os.path.exists(_caminho_da_foto(client, criada["foto"]))


def test_remove_a_vantagem_e_a_foto(client, empresa):
    criada = _cadastrar(client, empresa, foto=_foto()).get_json()

    resp = client.delete(f"/api/vantagens/{criada['id']}", headers=empresa)

    assert resp.status_code == 204
    assert client.get("/api/vantagens/minhas", headers=empresa).get_json() == []
    assert not os.path.exists(_caminho_da_foto(client, criada["foto"]))


def test_nao_edita_nem_remove_vantagem_de_outra_empresa(client, entrar, empresa):
    client.post("/api/empresas", json=OUTRA_EMPRESA)
    criada = _cadastrar(client, empresa).get_json()
    outra = entrar(OUTRA_EMPRESA["email"])

    editar = client.put(
        f"/api/vantagens/{criada['id']}",
        data=VANTAGEM,
        headers=outra,
        content_type="multipart/form-data",
    )

    assert editar.status_code == 404
    assert client.delete(f"/api/vantagens/{criada['id']}", headers=outra).status_code == 404
    assert len(client.get("/api/vantagens/minhas", headers=empresa).get_json()) == 1


def test_aluno_ve_o_catalogo_de_todas_as_empresas(client, entrar, empresa):
    client.post("/api/empresas", json=OUTRA_EMPRESA)
    client.post("/api/alunos", json=ALUNO)
    _cadastrar(client, empresa, nome="Livro", custo="300")
    _cadastrar(client, entrar(OUTRA_EMPRESA["email"]), nome="Lanche", custo="20")

    resp = client.get("/api/vantagens", headers=entrar(ALUNO["email"]))

    assert resp.status_code == 200
    assert [(v["nome"], v["empresaNome"]) for v in resp.get_json()] == [
        ("Lanche", "Cantina"),
        ("Livro", "Livraria"),
    ]


def test_catalogo_exige_login_de_aluno(client, empresa):
    assert client.get("/api/vantagens").status_code == 401
    assert client.get("/api/vantagens", headers=empresa).status_code == 403


def test_nao_remove_empresa_com_vantagens(client, empresa):
    _cadastrar(client, empresa)
    empresa_id = client.get("/api/auth/eu", headers=empresa).get_json()["id"]

    assert client.delete(f"/api/empresas/{empresa_id}").status_code == 409

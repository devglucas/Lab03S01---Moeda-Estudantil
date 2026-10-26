"""Testes dos services sem banco: os repositórios são trocados por fakes."""
import pytest

from app.services.empresa_service import EmpresaService
from app.services.erros import Conflito, DadosInvalidos, NaoEncontrado

EMPRESA = {
    "nome": "Livraria Central",
    "email": "Contato@Livraria.com",
    "cnpj": "12.345.678/0001-90",
    "senha": "senha123",
}


class RepositorioFake:
    def __init__(self, logins=(), cnpjs=()):
        self.salvos = []
        self.logins = set(logins)
        self.cnpjs = set(cnpjs)

    def salvar(self, entidade):
        self.salvos.append(entidade)
        return entidade

    def buscar_por_id(self, id_):
        return None

    def login_em_uso(self, login, exceto_id=None):
        return login in self.logins

    def cnpj_em_uso(self, cnpj, exceto_id=None):
        return cnpj in self.cnpjs


def servico(**fakes):
    repo = RepositorioFake(**fakes)
    return EmpresaService(empresas=repo, usuarios=repo), repo


def test_criar_normaliza_e_salva():
    empresas, repo = servico()
    empresa = empresas.criar(EMPRESA)

    assert repo.salvos == [empresa]
    assert empresa.email == empresa.login == "contato@livraria.com"
    assert empresa.cnpj == "12345678000190"
    assert empresa.senha_hash != EMPRESA["senha"]
    assert empresa.verificar_senha(EMPRESA["senha"])


def test_criar_com_dados_invalidos_nao_salva():
    empresas, repo = servico()
    with pytest.raises(DadosInvalidos) as erro:
        empresas.criar({**EMPRESA, "email": "sem-arroba", "cnpj": "1"})

    assert erro.value.campos.keys() == {"email", "cnpj"}
    assert repo.salvos == []


def test_email_em_uso_por_outro_perfil():
    empresas, _ = servico(logins={"contato@livraria.com"})
    with pytest.raises(Conflito):
        empresas.criar(EMPRESA)


def test_buscar_inexistente():
    empresas, _ = servico()
    with pytest.raises(NaoEncontrado):
        empresas.buscar(42)

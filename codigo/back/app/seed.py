"""Dados iniciais: instituições de ensino pré-cadastradas no sistema."""
from app.models.instituicao import InstituicaoEnsino
from app.repositories import InstituicaoRepository

INSTITUICOES = [
    "PUC Minas",
    "UFMG",
    "CEFET-MG",
]


def seed_data():
    """Cadastra as instituições somente se a tabela ainda estiver vazia."""
    instituicoes = InstituicaoRepository()
    if not instituicoes.esta_vazio():
        return

    instituicoes.salvar_varias(InstituicaoEnsino(nome=nome) for nome in INSTITUICOES)

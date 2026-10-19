"""Dados iniciais: instituições de ensino pré-cadastradas no sistema."""
from app.extensions import db
from app.models.instituicao import InstituicaoEnsino

INSTITUICOES = [
    "PUC Minas",
    "UFMG",
    "CEFET-MG",
]


def seed_data():
    """Cadastra as instituições somente se a tabela ainda estiver vazia."""
    if InstituicaoEnsino.query.first() is not None:
        return

    db.session.add_all(InstituicaoEnsino(nome=nome) for nome in INSTITUICOES)
    db.session.commit()

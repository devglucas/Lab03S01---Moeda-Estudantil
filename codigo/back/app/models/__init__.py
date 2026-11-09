"""Importa todos os models para registrá-los no metadata do SQLAlchemy."""
from app.models.usuario import Usuario
from app.models.instituicao import InstituicaoEnsino
from app.models.aluno import Aluno
from app.models.empresa import EmpresaParceira
from app.models.professor import Professor
from app.models.transacao import EnvioMoeda, Transacao, TrocaVantagem

__all__ = [
    "Usuario",
    "InstituicaoEnsino",
    "Aluno",
    "EmpresaParceira",
    "Professor",
    "Transacao",
    "EnvioMoeda",
    "TrocaVantagem",
]

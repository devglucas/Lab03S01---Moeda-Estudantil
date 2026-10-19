"""Importa todos os models para registrá-los no metadata do SQLAlchemy."""
from app.models.usuario import Usuario
from app.models.instituicao import InstituicaoEnsino
from app.models.aluno import Aluno
from app.models.empresa import EmpresaParceira

__all__ = ["Usuario", "InstituicaoEnsino", "Aluno", "EmpresaParceira"]

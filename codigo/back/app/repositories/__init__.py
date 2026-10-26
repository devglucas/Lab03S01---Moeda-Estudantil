"""Camada de repositório: único ponto de acesso ao banco de dados.

Os services pedem e gravam entidades por aqui, sem montar consultas nem
controlar a sessão do SQLAlchemy diretamente.
"""
from app.repositories.base_repository import ErroIntegridade
from app.repositories.usuario_repository import UsuarioRepository
from app.repositories.instituicao_repository import InstituicaoRepository
from app.repositories.aluno_repository import AlunoRepository
from app.repositories.empresa_repository import EmpresaRepository

__all__ = [
    "ErroIntegridade",
    "UsuarioRepository",
    "InstituicaoRepository",
    "AlunoRepository",
    "EmpresaRepository",
]

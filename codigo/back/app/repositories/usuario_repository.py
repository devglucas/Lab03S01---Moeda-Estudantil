"""Repositório dos usuários (dados de login comuns a todos os perfis)."""
from app.models.usuario import Usuario
from app.repositories.base_repository import BaseRepository


class UsuarioRepository(BaseRepository):
    model = Usuario

    def login_em_uso(self, login, exceto_id=None):
        """O login (e-mail) é único entre alunos, professores e empresas."""
        return self._existe(Usuario.login, login, exceto_id)

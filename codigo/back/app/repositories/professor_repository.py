"""Repositório dos alunos."""
from app.models.professor import Professor
from app.repositories.base_repository import BaseRepository

class ErroIntegridade(Exception):
    """O banco recusou a gravação (chave única ou estrangeira violada)."""
    
class ProfessorRepository(BaseRepository):
    model = Professor

    def listar(self):
        return Professor.query.order_by(Professor.nome).all()

    def cpf_em_uso(self, cpf, exceto_id=None):
        return self._existe(Professor.cpf, cpf, exceto_id)

    def existe_na_instituicao(self, instituicao_id):
        return self._existe(Professor.instituicao_id, instituicao_id)

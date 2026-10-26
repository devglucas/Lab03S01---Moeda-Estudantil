"""Repositório dos alunos."""
from app.models.aluno import Aluno
from app.repositories.base_repository import BaseRepository


class AlunoRepository(BaseRepository):
    model = Aluno

    def listar(self):
        return Aluno.query.order_by(Aluno.nome).all()

    def cpf_em_uso(self, cpf, exceto_id=None):
        return self._existe(Aluno.cpf, cpf, exceto_id)

    def existe_na_instituicao(self, instituicao_id):
        return self._existe(Aluno.instituicao_id, instituicao_id)

"""Repositório das instituições de ensino."""
from app.extensions import db
from app.models.instituicao import InstituicaoEnsino
from app.repositories.base_repository import BaseRepository


class InstituicaoRepository(BaseRepository):
    model = InstituicaoEnsino

    def listar(self):
        return InstituicaoEnsino.query.order_by(InstituicaoEnsino.nome).all()

    def nome_em_uso(self, nome, exceto_id=None):
        return self._existe(InstituicaoEnsino.nome, nome, exceto_id)

    def esta_vazio(self):
        return InstituicaoEnsino.query.first() is None

    def salvar_varias(self, instituicoes):
        db.session.add_all(instituicoes)
        self._confirmar()

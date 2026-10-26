"""Operações de persistência comuns a todos os repositórios."""
from sqlalchemy.exc import IntegrityError

from app.extensions import db


class ErroIntegridade(Exception):
    """O banco recusou a gravação (chave única ou estrangeira violada)."""


class BaseRepository:
    model = None

    def buscar_por_id(self, id_):
        return db.session.get(self.model, id_)

    def salvar(self, entidade):
        db.session.add(entidade)
        self._confirmar()
        return entidade

    def remover(self, entidade):
        db.session.delete(entidade)
        self._confirmar()

    def _confirmar(self):
        try:
            db.session.commit()
        except IntegrityError as erro:
            db.session.rollback()
            raise ErroIntegridade() from erro

    def _existe(self, coluna, valor, exceto_id=None):
        """Diz se outro registro já usa ``valor`` em ``coluna``."""
        consulta = self.model.query.filter(coluna == valor)
        if exceto_id is not None:
            consulta = consulta.filter(self.model.id != exceto_id)
        return db.session.query(consulta.exists()).scalar()

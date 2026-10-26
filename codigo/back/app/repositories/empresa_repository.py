"""Repositório das empresas parceiras."""
from app.models.empresa import EmpresaParceira
from app.repositories.base_repository import BaseRepository


class EmpresaRepository(BaseRepository):
    model = EmpresaParceira

    def listar(self):
        return EmpresaParceira.query.order_by(EmpresaParceira.nome).all()

    def cnpj_em_uso(self, cnpj, exceto_id=None):
        return self._existe(EmpresaParceira.cnpj, cnpj, exceto_id)

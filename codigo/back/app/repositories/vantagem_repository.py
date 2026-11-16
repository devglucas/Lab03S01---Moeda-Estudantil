"""Repositório das vantagens oferecidas pelas empresas parceiras."""
from app.models.vantagem import Vantagem
from app.repositories.base_repository import BaseRepository


class VantagemRepository(BaseRepository):
    model = Vantagem

    def listar_todas(self):
        """Catálogo do aluno: das mais baratas para as mais caras."""
        return Vantagem.query.order_by(Vantagem.custo, Vantagem.nome).all()

    def listar_por_empresa(self, empresa_id):
        """Vantagens de uma empresa, das cadastradas mais recentemente primeiro."""
        return (
            Vantagem.query.filter_by(empresa_id=empresa_id)
            .order_by(Vantagem.id.desc())
            .all()
        )

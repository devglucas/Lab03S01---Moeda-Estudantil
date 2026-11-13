from app.extensions import db
from app.models.vantagem import Vantagem


class VantagemRepository:
    # def registrar(self, vantagem, *entidades_alteradas):
    #     db.session.add(vantagem)
    #     # for entidade in entidades_alteradas:
    #     #     db.session.add(entidade)
    #     # db.session.commit()
    #     return vantagem

    
    def criar(self, vantagem):
        # Associa o id da empresa na vantagem
        # vantagem.empresa_id = empresa_id
        
        # O SQLAlchemy agora recebe um objeto mapeado (Vantagem), resolvendo o erro anterior!
        db.session.add(vantagem)
        db.session.commit()
        return vantagem
    
    def listar_todas(self):
        return Vantagem.query.order_by(Vantagem.empresa_id.desc()).all()
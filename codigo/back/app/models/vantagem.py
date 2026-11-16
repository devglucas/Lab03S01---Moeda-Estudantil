from app.extensions import db
from app.models.empresa import EmpresaParceira

class Vantagem(db.Model):
    __tablename__ = "vantagens"

    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(32), nullable=False)
    descricao = db.Column(db.String(144), nullable=True)
    custo = db.Column(db.Integer, nullable=False)
    foto = db.Column(db.String(255), nullable=True)

    empresa_id = db.Column(db.Integer, db.ForeignKey("empresas_parceiras.id"), nullable=False)
    
    # Relacionamento
    empresa = db.relationship("EmpresaParceira", backref="vantagens")

    def to_dict(self):
        return {
            "id": self.id,
            "nome": self.nome,
            "descricao": self.descricao,
            "custo": self.custo,
            "empresaId": self.empresa_id,
            "empresaNome": self.empresa.nome if self.empresa else None,
            "foto": self.foto,
            "fotoUrl": (
                f"http://localhost:5000/uploads/{self.foto}"
                if self.foto else None
            )
        }
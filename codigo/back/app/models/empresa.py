"""Model das empresas parceiras (oferecem vantagens em troca de moedas)."""
from app.extensions import db
from app.models.usuario import Usuario


class EmpresaParceira(Usuario):
    __tablename__ = "empresas_parceiras"

    id = db.Column(db.Integer, db.ForeignKey("usuarios.id"), primary_key=True)

    nome = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(160), nullable=False, unique=True)

    __mapper_args__ = {"polymorphic_identity": "empresa"}

    def to_dict(self):
        return {
            "id": self.id,
            "nome": self.nome,
            "email": self.email,
            "login": self.login,
        }
"""Model das vantagens que as empresas parceiras oferecem em troca de moedas."""
from app.extensions import db


class Vantagem(db.Model):
    __tablename__ = "vantagens"

    id = db.Column(db.Integer, primary_key=True)

    nome = db.Column(db.String(120), nullable=False)
    descricao = db.Column(db.String(500), nullable=False)
    custo = db.Column(db.Integer, nullable=False)  # em moedas
    foto = db.Column(db.String(255), nullable=True)  # nome do arquivo em UPLOAD_FOLDER

    empresa_id = db.Column(db.Integer, db.ForeignKey("empresas_parceiras.id"), nullable=False)
    empresa = db.relationship("EmpresaParceira", backref="vantagens")

    def to_dict(self):
        return {
            "id": self.id,
            "nome": self.nome,
            "descricao": self.descricao,
            "custo": self.custo,
            "foto": self.foto,
            "empresaId": self.empresa_id,
            "empresaNome": self.empresa.nome,
        }

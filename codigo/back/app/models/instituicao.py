"""Model das instituições de ensino (pré-cadastradas no sistema)."""
from app.extensions import db


class InstituicaoEnsino(db.Model):
    __tablename__ = "instituicoes_ensino"

    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(160), nullable=False, unique=True)

    alunos = db.relationship("Aluno", back_populates="instituicao")
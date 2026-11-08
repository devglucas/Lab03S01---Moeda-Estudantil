"""Model das transações: envio de moedas de um professor a um aluno."""
from datetime import datetime, timezone

from app.extensions import db


class Transacao(db.Model):
    __tablename__ = "transacoes"

    id = db.Column(db.Integer, primary_key=True)
    valor = db.Column(db.Integer, nullable=False)
    mensagem = db.Column(db.String(500), nullable=False)
    data = db.Column(
        db.DateTime, nullable=False, default=lambda: datetime.now(timezone.utc)
    )

    professor_id = db.Column(db.Integer, db.ForeignKey("professores.id"), nullable=False)
    aluno_id = db.Column(db.Integer, db.ForeignKey("alunos.id"), nullable=False)

    professor = db.relationship("Professor")
    aluno = db.relationship("Aluno")

    def to_dict(self):
        return {
            "id": self.id,
            "valor": self.valor,
            "mensagem": self.mensagem,
            "data": self.data.isoformat(),
            "professorId": self.professor_id,
            "professorNome": self.professor.nome,
            "alunoId": self.aluno_id,
            "alunoNome": self.aluno.nome,
        }
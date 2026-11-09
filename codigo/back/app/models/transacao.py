"""Models das transações de moedas.

``Transacao`` é a superclasse abstrata de ``EnvioMoeda`` (professor -> aluno) e
``TrocaVantagem`` (aluno -> vantagem). Usa herança de tabela unida, como
``Usuario``: a tabela ``transacoes`` guarda o que é comum e cada tipo tem a sua.
O aluno fica na superclasse porque toda transação envolve um aluno, e assim o
extrato dele é uma única consulta que traz os dois tipos.
"""
from datetime import datetime, timezone

from app.extensions import db


class Transacao(db.Model):
    __tablename__ = "transacoes"

    id = db.Column(db.Integer, primary_key=True)
    tipo = db.Column(db.String(20), nullable=False)  # "envio" | "troca"
    valor = db.Column(db.Integer, nullable=False)
    data = db.Column(
        db.DateTime, nullable=False, default=lambda: datetime.now(timezone.utc)
    )

    aluno_id = db.Column(db.Integer, db.ForeignKey("alunos.id"), nullable=False)
    aluno = db.relationship("Aluno")

    __mapper_args__ = {"polymorphic_on": tipo, "with_polymorphic": "*"}

    def to_dict(self):
        # O SQLite devolve a data sem fuso; ela é sempre gravada em UTC.
        data = self.data.replace(tzinfo=timezone.utc)
        return {
            "id": self.id,
            "tipo": self.tipo,
            "valor": self.valor,
            "data": data.isoformat(),
            "alunoId": self.aluno_id,
            "alunoNome": self.aluno.nome,
        }


class EnvioMoeda(Transacao):
    __tablename__ = "envios_moeda"

    id = db.Column(db.Integer, db.ForeignKey("transacoes.id"), primary_key=True)
    mensagem = db.Column(db.String(500), nullable=False)

    professor_id = db.Column(db.Integer, db.ForeignKey("professores.id"), nullable=False)
    professor = db.relationship("Professor")

    __mapper_args__ = {"polymorphic_identity": "envio"}

    def to_dict(self):
        return {
            **super().to_dict(),
            "mensagem": self.mensagem,
            "professorId": self.professor_id,
            "professorNome": self.professor.nome,
        }


class TrocaVantagem(Transacao):
    """Troca de moedas por vantagem. A ligação com a vantagem entra junto com o
    cadastro de vantagens; por enquanto só existe o código do cupom."""

    __tablename__ = "trocas_vantagem"

    id = db.Column(db.Integer, db.ForeignKey("transacoes.id"), primary_key=True)
    codigo = db.Column(db.String(20), nullable=False, unique=True)

    __mapper_args__ = {"polymorphic_identity": "troca"}

    def to_dict(self):
        return {**super().to_dict(), "codigo": self.codigo}

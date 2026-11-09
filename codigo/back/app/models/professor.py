"""Model dos professores (cadastro, saldo de moedas e instituição de ensino).

O professor é um ``Usuario``: herda ``login`` (o e-mail) e ``senha_hash``. O ``saldo``
é sempre alterado pelo crédito do semestre e pelos envios de moedas, nunca direto
pela tela de cadastro.
"""
from app.extensions import db
from app.models.usuario import Usuario


class Professor(Usuario):
    __tablename__ = "professores"

    id = db.Column(db.Integer, db.ForeignKey("usuarios.id"), primary_key=True)

    nome = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(160), nullable=False, unique=True)
    cpf = db.Column(db.String(11), nullable=False, unique=True)  # só dígitos
    departamento = db.Column(db.String(120), nullable=False)
    saldo = db.Column(db.Integer, nullable=False, default=0)

    instituicao_id = db.Column(
        db.Integer, db.ForeignKey("instituicoes_ensino.id"), nullable=False
    )
    instituicao = db.relationship("InstituicaoEnsino", back_populates="professores")

    __mapper_args__ = {"polymorphic_identity": "professor"}

    def receber_moedas_semestre(self):
        self.saldo += 1000

    def debitar(self, valor):
        if valor > self.saldo:
            raise ValueError("Saldo insuficiente")
        self.saldo -= valor

    def to_dict(self):
        return {
            "id": self.id,
            "nome": self.nome,
            "email": self.email,
            "cpf": self.cpf,
            "departamento": self.departamento,
            "saldo": self.saldo,
            "instituicaoId": self.instituicao_id,
            "instituicaoNome": self.instituicao.nome
        }
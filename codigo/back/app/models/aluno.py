"""Model dos alunos (cadastro, saldo de moedas e instituição de ensino).

O aluno é um ``Usuario``: herda ``login`` (o e-mail) e ``senha_hash``. O ``saldo`` é
sempre alterado por transações (recebimento de moedas e troca por vantagem),
nunca direto pela tela de cadastro.
"""
from app.extensions import db
from app.models.usuario import Usuario


class Aluno(Usuario):
    __tablename__ = "alunos"

    id = db.Column(db.Integer, db.ForeignKey("usuarios.id"), primary_key=True)

    nome = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(160), nullable=False, unique=True)
    cpf = db.Column(db.String(11), nullable=False, unique=True)  # só dígitos
    rg = db.Column(db.String(20), nullable=False)
    endereco = db.Column(db.String(255), nullable=False)
    curso = db.Column(db.String(120), nullable=False)
    saldo = db.Column(db.Integer, nullable=False, default=0)

    instituicao_id = db.Column(
        db.Integer, db.ForeignKey("instituicoes_ensino.id"), nullable=False
    )
    instituicao = db.relationship("InstituicaoEnsino", back_populates="alunos")

    __mapper_args__ = {"polymorphic_identity": "aluno"}

    def receber_moedas(self, valor):
        self.saldo += valor

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
            "rg": self.rg,
            "endereco": self.endereco,
            "curso": self.curso,
            "saldo": self.saldo,
            "instituicaoId": self.instituicao_id,
            "instituicaoNome": self.instituicao.nome,
        }
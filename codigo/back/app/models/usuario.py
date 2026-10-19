"""Model base dos usuários do sistema de moeda estudantil (login e senha).

``Usuario`` é a superclasse de ``Aluno``, ``Professor`` e ``EmpresaParceira``.
Usa herança de tabela unida (joined): a tabela ``usuarios`` guarda o que é
comum e cada perfil tem a sua própria tabela. Assim o login é único entre
todos os tipos de usuário.
"""
from werkzeug.security import check_password_hash, generate_password_hash

from app.extensions import db


class Usuario(db.Model):
    __tablename__ = "usuarios"

    id = db.Column(db.Integer, primary_key=True)

    # Credenciais (autenticação exigida para todos os perfis).
    login = db.Column(db.String(50), nullable=False, unique=True)
    senha_hash = db.Column(db.String(255), nullable=False)

    # Discriminador da herança: "aluno" | "professor" | "empresa".
    tipo = db.Column(db.String(20), nullable=False)

    __mapper_args__ = {
        "polymorphic_on": tipo,
        "polymorphic_identity": "usuario",
    }

    def definir_senha(self, senha):
        self.senha_hash = generate_password_hash(senha)

    def verificar_senha(self, senha):
        return check_password_hash(self.senha_hash, senha)
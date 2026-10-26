"""Fábrica da aplicação Flask (arquitetura MVC em camadas).

Monta a app, inicializa o banco (SQLite), libera CORS para o front em dev,
registra os blueprints (alunos, empresas e instituições), converte os erros
dos services em respostas JSON e semeia as instituições de ensino
pré-cadastradas quando a base ainda está vazia.

Camadas: controllers (HTTP) -> services (regras) -> repositories (banco) -> models.
"""
import os

from dotenv import load_dotenv
from flask import Flask, jsonify
from flask_cors import CORS

from app.extensions import db
from app.services.erros import ErroDeNegocio

load_dotenv(os.path.join(os.path.dirname(os.path.dirname(__file__)), ".env"))


def create_app():
    app = Flask(__name__)

    # DATABASE_URL permite apontar para outra base — os testes usam SQLite em
    # memória para não recriar (e apagar) o banco de desenvolvimento.
    basedir = os.path.abspath(os.path.dirname(__file__))
    db_path = os.path.join(basedir, "..", "moedas.db")
    app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get(
        "DATABASE_URL", f"sqlite:///{db_path}"
    )
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    app.config["JSON_AS_ASCII"] = False

    db.init_app(app)

    # Libera a origem do front (Vite) em desenvolvimento. O header Authorization
    # precisa ser aceito para o token de sessão chegar à API.
    frontend_origin = os.environ.get("FRONTEND_ORIGIN", "http://localhost:5173")
    CORS(
        app,
        resources={r"/api/*": {"origins": frontend_origin}},
        allow_headers=["Content-Type", "Authorization"],
    )

    from app.controllers.aluno_controller import aluno_bp
    from app.controllers.empresa_controller import empresa_bp
    from app.controllers.instituicao_controller import instituicao_bp

    app.register_blueprint(aluno_bp)
    app.register_blueprint(empresa_bp)
    app.register_blueprint(instituicao_bp)

    # Os services lançam ErroDeNegocio; aqui ele vira {"erro", "campos"} + status.
    @app.errorhandler(ErroDeNegocio)
    def erro_de_negocio(erro):
        return jsonify(erro.to_dict()), erro.status

    # Cria as tabelas que ainda não existem e preserva os dados já gravados.
    with app.app_context():
        from app import models  # noqa: F401  (registra as tabelas no metadata)
        from app.seed import seed_data

        db.create_all()
        seed_data()

    return app
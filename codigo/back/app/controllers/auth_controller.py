"""Controller da autenticação: login e perfil do usuário logado em /api/auth."""
from flask import Blueprint, g, jsonify, request

from app.autenticacao import exige_perfil
from app.services.auth_service import AuthService, perfil_json

auth_bp = Blueprint("auth", __name__, url_prefix="/api/auth")
servico = AuthService()


@auth_bp.post("/login")
def entrar():
    return jsonify(servico.entrar(request.get_json(silent=True)))


@auth_bp.get("/eu")
@exige_perfil()
def eu():
    return jsonify(perfil_json(g.usuario))

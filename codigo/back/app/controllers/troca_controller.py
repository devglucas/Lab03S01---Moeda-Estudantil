"""Controller da troca de vantagens em /api/trocas.

O aluno logado troca moedas por uma vantagem; a empresa logada consulta as
trocas das próprias vantagens para conferir os cupons apresentados.
"""
from flask import Blueprint, g, jsonify, request

from app.autenticacao import exige_perfil
from app.services.troca_service import TrocaService

troca_bp = Blueprint("trocas", __name__, url_prefix="/api/trocas")
servico = TrocaService()


@troca_bp.post("")
@exige_perfil("aluno")
def trocar():
    troca = servico.trocar(g.usuario, request.get_json(silent=True))
    return jsonify(troca.to_dict()), 201


@troca_bp.get("")
@exige_perfil("empresa")
def listar_da_empresa():
    return jsonify([troca.to_dict() for troca in servico.trocas_da_empresa(g.usuario)])

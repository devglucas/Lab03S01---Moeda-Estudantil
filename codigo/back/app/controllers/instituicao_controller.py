"""Controller das instituições de ensino: CRUD em /api/instituicoes.

Só traduz HTTP <-> Python; as regras ficam em ``InstituicaoService``.
"""
from flask import Blueprint, jsonify, request

from app.services.instituicao_service import InstituicaoService


instituicao_bp = Blueprint(
    "instituicoes",
    __name__,
    url_prefix="/api/instituicoes",
)
servico = InstituicaoService()


@instituicao_bp.post("")
def criar():
    instituicao = servico.criar(request.get_json(silent=True))
    return jsonify(instituicao.to_dict()), 201


@instituicao_bp.get("")
def listar():
    return jsonify([instituicao.to_dict() for instituicao in servico.listar()])


@instituicao_bp.get("/<int:instituicao_id>")
def buscar(instituicao_id):
    return jsonify(servico.buscar(instituicao_id).to_dict())


@instituicao_bp.put("/<int:instituicao_id>")
def atualizar(instituicao_id):
    instituicao = servico.atualizar(instituicao_id, request.get_json(silent=True))
    return jsonify(instituicao.to_dict())


@instituicao_bp.delete("/<int:instituicao_id>")
def remover(instituicao_id):
    servico.remover(instituicao_id)
    return "", 204

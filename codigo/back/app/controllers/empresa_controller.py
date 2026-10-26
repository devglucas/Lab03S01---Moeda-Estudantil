"""Controller das empresas parceiras: CRUD em /api/empresas.

Só traduz HTTP <-> Python; as regras ficam em ``EmpresaService``.
"""
from flask import Blueprint, jsonify, request

from app.services.empresa_service import EmpresaService


empresa_bp = Blueprint("empresas", __name__, url_prefix="/api/empresas")
servico = EmpresaService()


@empresa_bp.post("")
def criar():
    empresa = servico.criar(request.get_json(silent=True))
    return jsonify(empresa.to_dict()), 201


@empresa_bp.get("")
def listar():
    return jsonify([empresa.to_dict() for empresa in servico.listar()])


@empresa_bp.get("/<int:empresa_id>")
def buscar(empresa_id):
    return jsonify(servico.buscar(empresa_id).to_dict())


@empresa_bp.put("/<int:empresa_id>")
def atualizar(empresa_id):
    empresa = servico.atualizar(empresa_id, request.get_json(silent=True))
    return jsonify(empresa.to_dict())


@empresa_bp.delete("/<int:empresa_id>")
def remover(empresa_id):
    servico.remover(empresa_id)
    return "", 204

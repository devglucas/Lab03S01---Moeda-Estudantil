"""Controller dos alunos: CRUD em /api/alunos.

Só traduz HTTP <-> Python; as regras ficam em ``AlunoService``.
"""
from flask import Blueprint, jsonify, request

from app.services.aluno_service import AlunoService


aluno_bp = Blueprint("alunos", __name__, url_prefix="/api/alunos")
servico = AlunoService()


@aluno_bp.post("")
def criar():
    aluno = servico.criar(request.get_json(silent=True))
    return jsonify(aluno.to_dict()), 201


@aluno_bp.get("")
def listar():
    return jsonify([aluno.to_dict() for aluno in servico.listar()])


@aluno_bp.get("/<int:aluno_id>")
def buscar(aluno_id):
    return jsonify(servico.buscar(aluno_id).to_dict())


@aluno_bp.put("/<int:aluno_id>")
def atualizar(aluno_id):
    aluno = servico.atualizar(aluno_id, request.get_json(silent=True))
    return jsonify(aluno.to_dict())


@aluno_bp.delete("/<int:aluno_id>")
def remover(aluno_id):
    servico.remover(aluno_id)
    return "", 204

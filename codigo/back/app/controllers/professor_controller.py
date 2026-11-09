"""Controller dos professores: cadastro e consulta.

Só traduz HTTP <-> Python; as regras ficam em ``ProfessorService``.
"""
from flask import Blueprint, jsonify, request

from app.services.professor_service import ProfessorService

professor_bp = Blueprint("professores", __name__, url_prefix="/api/professores")
servico = ProfessorService()


@professor_bp.post("")
def criar():
    professor = servico.criar(request.get_json(silent=True))
    return jsonify(professor.to_dict()), 201


@professor_bp.get("")
def listar():
    return jsonify([professor.to_dict() for professor in servico.listar()])


@professor_bp.get("/<int:professor_id>")
def buscar(professor_id):
    return jsonify(servico.buscar(professor_id).to_dict())

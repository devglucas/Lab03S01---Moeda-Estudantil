"""Controller dos professores: cadastro, consulta, crédito e envio de moedas.

Só traduz HTTP <-> Python; as regras ficam em ``ProfessorService`` e ``TransacaoService``.
"""
from flask import Blueprint, jsonify, request

from app.services.professor_service import ProfessorService
from app.services.transacao_service import TransacaoService

professor_bp = Blueprint("professores", __name__, url_prefix="/api/professores")
servico = ProfessorService()
servico_transacao = TransacaoService()


@professor_bp.post("")
def criar():
    professor = servico.criar(request.get_json(silent=True))
    enviar_moedas(professor.id)
    return jsonify(professor.to_dict()), 201


@professor_bp.get("")
def listar():
    return jsonify([professor.to_dict() for professor in servico.listar()])


@professor_bp.get("/<int:professor_id>")
def buscar(professor_id):
    return jsonify(servico.buscar(professor_id).to_dict())


# @professor_bp.post("/<int:professor_id>/recebe-1000")
def recebe1000(professor_id):
    professor = servico_transacao.recebe1000(professor_id)
    return jsonify(professor.to_dict())


@professor_bp.post("/<int:professor_id>/enviar-moedas")
def enviar_moedas(professor_id):
    transacao = servico_transacao.enviar_moedas(
        professor_id, request.get_json(silent=True)
    )
    return jsonify(transacao.to_dict()), 201
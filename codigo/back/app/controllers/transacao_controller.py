"""Controller das transações: envio de moedas e extrato em /api/transacoes.

Só traduz HTTP <-> Python; as regras ficam em ``TransacaoService``.
"""
from flask import Blueprint, jsonify, request

from app.services.transacao_service import TransacaoService

transacao_bp = Blueprint("transacoes", __name__, url_prefix="/api/transacoes")
servico = TransacaoService()


def _extrato_json(extrato):
    return {
        "saldo": extrato["saldo"],
        "transacoes": [transacao.to_dict() for transacao in extrato["transacoes"]],
    }


@transacao_bp.get("")
def listar():
    return jsonify([transacao.to_dict() for transacao in servico.listar_todas()])


@transacao_bp.post("")
def enviar_moedas():
    envio = servico.enviar_moedas(request.get_json(silent=True))
    return jsonify(envio.to_dict()), 201


@transacao_bp.get("/extrato/professor/<int:professor_id>")
def extrato_professor(professor_id):
    return jsonify(_extrato_json(servico.extrato_professor(professor_id)))


@transacao_bp.get("/extrato/aluno/<int:aluno_id>")
def extrato_aluno(aluno_id):
    return jsonify(_extrato_json(servico.extrato_aluno(aluno_id)))

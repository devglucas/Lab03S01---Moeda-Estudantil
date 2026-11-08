from flask import Blueprint, jsonify, request

# from app.services.professor_service import NaoEncontradoError, ValidacaoError
from app.services.transacao_service import TransacaoService

transacao_bp = Blueprint("transacoes", __name__, url_prefix="/transacoes")
service = TransacaoService()


# @transacao_bp.errorhandler(ValidacaoError)
# def _validacao(e):
#     return jsonify({"erro": str(e)}), 400


# @transacao_bp.errorhandler(NaoEncontradoError)
# def _nao_encontrado(e):
#     return jsonify({"erro": str(e)}), 404


def _extrato_json(extrato):
    return {
        "saldo": extrato["saldo"],
        "transacoes": [t.to_dict() for t in extrato["transacoes"]],
    }

@transacao_bp.get("")
def buscar_todas_transacoes():
    # Com autenticação, professorId deve vir do usuário logado, não do corpo.
    transacao = service.enviar_moedas(request.get_json(silent=True) or {})
    return jsonify(transacao.to_dict()), 201


@transacao_bp.post("")
def enviar_moedas():
    # Com autenticação, professorId deve vir do usuário logado, não do corpo.
    transacao = service.enviar_moedas(request.get_json(silent=True) or {})
    return jsonify(transacao.to_dict()), 201


@transacao_bp.get("/extrato/professor/<int:professor_id>")
def extrato_professor(professor_id):
    return jsonify(_extrato_json(service.extrato_professor(professor_id)))


@transacao_bp.get("/extrato/aluno/<int:aluno_id>")
def extrato_aluno(aluno_id):
    return jsonify(_extrato_json(service.extrato_aluno(aluno_id)))
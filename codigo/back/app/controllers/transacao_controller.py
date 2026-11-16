"""Controller das transações: envio de moedas e extrato em /api/transacoes.

Só traduz HTTP <-> Python; as regras ficam em ``TransacaoService``. As duas
rotas usam o usuário logado: o professor envia moedas em seu próprio nome e
cada usuário só consulta o próprio extrato.
"""
from flask import Blueprint, g, jsonify, request

from app.autenticacao import exige_perfil
from app.services.transacao_service import TransacaoService

transacao_bp = Blueprint("transacoes", __name__, url_prefix="/api/transacoes")
servico = TransacaoService()


def _extrato_json(extrato):
    return {
        "saldo": extrato["saldo"],
        "transacoes": [transacao.to_dict() for transacao in extrato["transacoes"]],
    }


@transacao_bp.post("")
@exige_perfil("professor")
def enviar_moedas():
    envio = servico.enviar_moedas(g.usuario, request.get_json(silent=True))
    return jsonify(envio.to_dict()), 201


@transacao_bp.get("/extrato")
@exige_perfil("aluno", "professor")
def extrato():
    return jsonify(_extrato_json(servico.extrato(g.usuario)))

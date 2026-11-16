"""Controller das vantagens em /api/vantagens.

A empresa logada cadastra, edita e remove as próprias vantagens (formulário
multipart, por causa da foto); o aluno logado consulta o catálogo completo.
"""
from flask import Blueprint, g, jsonify, request

from app.autenticacao import exige_perfil
from app.services.vantagem_service import VantagemService

vantagem_bp = Blueprint("vantagens", __name__, url_prefix="/api/vantagens")
servico = VantagemService()


def _foto():
    arquivo = request.files.get("foto")
    return arquivo if arquivo and arquivo.filename else None


@vantagem_bp.get("")
@exige_perfil("aluno")
def listar():
    return jsonify([vantagem.to_dict() for vantagem in servico.listar_todas()])


@vantagem_bp.get("/minhas")
@exige_perfil("empresa")
def listar_minhas():
    return jsonify([vantagem.to_dict() for vantagem in servico.listar_da_empresa(g.usuario)])


@vantagem_bp.post("")
@exige_perfil("empresa")
def criar():
    vantagem = servico.criar(g.usuario, request.form.to_dict(), _foto())
    return jsonify(vantagem.to_dict()), 201


@vantagem_bp.put("/<int:vantagem_id>")
@exige_perfil("empresa")
def atualizar(vantagem_id):
    vantagem = servico.atualizar(g.usuario, vantagem_id, request.form.to_dict(), _foto())
    return jsonify(vantagem.to_dict())


@vantagem_bp.delete("/<int:vantagem_id>")
@exige_perfil("empresa")
def remover(vantagem_id):
    servico.remover(g.usuario, vantagem_id)
    return "", 204

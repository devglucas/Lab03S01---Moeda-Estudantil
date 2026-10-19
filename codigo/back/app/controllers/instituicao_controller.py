"""Controller das instituições de ensino: CRUD em /api/instituicoes."""
from flask import Blueprint, jsonify, request
from sqlalchemy.exc import IntegrityError

from app.extensions import db
from app.models.instituicao import InstituicaoEnsino


instituicao_bp = Blueprint(
    "instituicoes",
    __name__,
    url_prefix="/api/instituicoes",
)


def _erro(mensagem, status, campos=None):
    corpo = {"erro": mensagem}
    if campos:
        corpo["campos"] = campos
    return jsonify(corpo), status

def _buscar(instituicao_id):
    return db.session.get(InstituicaoEnsino, instituicao_id)

def nome_valido(dados):
    if not isinstance(dados, dict):
        return None, {"nome": "Envie os dados em JSON."}

    nome = dados.get("nome")

    if not isinstance(nome, str) or not nome.strip():
        return None, {"nome": "O nome é obrigatório."}

    nome = nome.strip()

    if len(nome) > 160:
        return None, {"nome": "O nome deve ter até 160 caracteres."}

    return nome, None

@instituicao_bp.post("")
def criar():
    dados = request.get_json(silent=True)
    nome, campos = nome_valido(dados)

    if campos:
        return _erro("Dados inválidos", 400, campos)

    existente = InstituicaoEnsino.query.filter_by(nome=nome).first()

    if existente:
        return _erro("Instituição já cadastrada", 409)

    instituicao = InstituicaoEnsino(nome=nome)
    db.session.add(instituicao)

    try:
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        return _erro("Instituição já cadastrada", 409)

    return jsonify({
        "id": instituicao.id,
        "nome": instituicao.nome,
    }), 201

@instituicao_bp.get("")
def listar():
    instituicoes = InstituicaoEnsino.query.order_by(
        InstituicaoEnsino.nome
    ).all()

    return jsonify([
        {"id": instituicao.id, "nome": instituicao.nome}
        for instituicao in instituicoes
    ])

@instituicao_bp.get("/<int:instituicao_id>")
def buscar(instituicao_id):
    instituicao = _buscar(instituicao_id)

    if instituicao is None:
        return _erro("Instituição não encontrada", 404)

    return jsonify({
        "id": instituicao.id,
        "nome": instituicao.nome,
    })

@instituicao_bp.put("/<int:instituicao_id>")
def atualizar(instituicao_id):
    instituicao = _buscar(instituicao_id)

    if instituicao is None:
        return _erro("Instituição não encontrada", 404)

    dados = request.get_json(silent=True)
    nome, campos = nome_valido(dados)

    if campos:
        return _erro("Dados inválidos", 400, campos)

    outra = InstituicaoEnsino.query.filter(
        InstituicaoEnsino.nome == nome,
        InstituicaoEnsino.id != instituicao_id,
    ).first()

    if outra:
        return _erro("Já existe uma instituição com esse nome", 409)

    instituicao.nome = nome

    try:
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        return _erro("Já existe uma instituição com esse nome", 409)

    return jsonify({
        "id": instituicao.id,
        "nome": instituicao.nome,
    })

@instituicao_bp.delete("/<int:instituicao_id>")
def remover(instituicao_id):
    instituicao = _buscar(instituicao_id)

    if instituicao is None:
        return _erro("Instituição não encontrada", 404)

    # Impede excluir instituições vinculadas a alunos.
    if instituicao.alunos:
        return _erro(
            "Não é possível remover uma instituição que possui alunos vinculados.",
            409,
        )

    db.session.delete(instituicao)

    try:
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        return _erro(
            "Não foi possível remover a instituição.",
            409,
        )

    return "", 204

"""Controller das empresas parceiras: CRUD em /api/empresas."""
from flask import Blueprint, jsonify, request
from sqlalchemy.exc import IntegrityError

from app.extensions import db
from app.models.empresa import EmpresaParceira
from app.models.usuario import Usuario
from app.validacao import (
    apenas_digitos,
    email_valido,
    faltantes,
    senha_valida,
    texto,
)


empresa_bp = Blueprint("empresas", __name__, url_prefix="/api/empresas")

CAMPOS_EMPRESA = ["nome", "email", "cnpj"]


def _erro(mensagem, status, campos=None):
    corpo = {"erro": mensagem}
    if campos:
        corpo["campos"] = campos
    return jsonify(corpo), status


def _buscar(empresa_id):
    return db.session.get(EmpresaParceira, empresa_id)


def _validar(dados, obrigatorios):
    campos = faltantes(dados, obrigatorios)

    if "email" not in campos and not email_valido(texto(dados, "email")):
        campos["email"] = "E-mail inválido"

    if "cnpj" not in campos and len(apenas_digitos(texto(dados, "cnpj"))) != 14:
        campos["cnpj"] = "O CNPJ deve ter 14 dígitos"

    # Na criação a senha é obrigatória; na edição só é validada se vier preenchida.
    senha = dados.get("senha")
    if "senha" not in campos and senha not in (None, "") and not senha_valida(senha):
        campos["senha"] = "A senha deve ter no mínimo 6 caracteres"

    return campos


# CREATE
@empresa_bp.post("")
def criar():
    dados = request.get_json(silent=True)
    if not isinstance(dados, dict):
        return _erro("Envie os dados em JSON.", 400)

    campos = _validar(dados, CAMPOS_EMPRESA + ["senha"])
    if campos:
        return _erro("Dados inválidos", 400, campos)

    email = texto(dados, "email").lower()
    cnpj = apenas_digitos(texto(dados, "cnpj"))

    # O e-mail é o login, então não pode se repetir em nenhum perfil.
    if Usuario.query.filter_by(login=email).first():
        return _erro("E-mail já cadastrado", 409)

    if EmpresaParceira.query.filter_by(cnpj=cnpj).first():
        return _erro("CNPJ já cadastrado", 409)

    empresa = EmpresaParceira(
        login=email,
        nome=texto(dados, "nome"),
        email=email,
        cnpj=cnpj,
    )
    empresa.definir_senha(dados["senha"])
    db.session.add(empresa)

    try:
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        return _erro("E-mail ou CNPJ já cadastrado", 409)

    return jsonify(empresa.to_dict()), 201


# READ - listar todas
@empresa_bp.get("")
def listar():
    empresas = EmpresaParceira.query.order_by(EmpresaParceira.nome).all()
    return jsonify([empresa.to_dict() for empresa in empresas])


# READ - buscar por ID
@empresa_bp.get("/<int:empresa_id>")
def buscar(empresa_id):
    empresa = _buscar(empresa_id)

    if empresa is None:
        return _erro("Empresa não encontrada", 404)

    return jsonify(empresa.to_dict())


# UPDATE
@empresa_bp.put("/<int:empresa_id>")
def atualizar(empresa_id):
    empresa = _buscar(empresa_id)

    if empresa is None:
        return _erro("Empresa não encontrada", 404)

    dados = request.get_json(silent=True)
    if not isinstance(dados, dict):
        return _erro("Envie os dados em JSON.", 400)

    campos = _validar(dados, CAMPOS_EMPRESA)
    if campos:
        return _erro("Dados inválidos", 400, campos)

    email = texto(dados, "email").lower()
    cnpj = apenas_digitos(texto(dados, "cnpj"))

    outro_email = Usuario.query.filter(
        Usuario.login == email,
        Usuario.id != empresa_id,
    ).first()

    if outro_email:
        return _erro("E-mail já cadastrado", 409)

    outro_cnpj = EmpresaParceira.query.filter(
        EmpresaParceira.cnpj == cnpj,
        EmpresaParceira.id != empresa_id,
    ).first()

    if outro_cnpj:
        return _erro("CNPJ já cadastrado", 409)

    empresa.nome = texto(dados, "nome")
    empresa.email = email
    empresa.login = email
    empresa.cnpj = cnpj

    senha = dados.get("senha")
    if senha:
        empresa.definir_senha(senha)

    try:
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        return _erro("E-mail ou CNPJ já cadastrado", 409)

    return jsonify(empresa.to_dict())


# DELETE
@empresa_bp.delete("/<int:empresa_id>")
def remover(empresa_id):
    empresa = _buscar(empresa_id)

    if empresa is None:
        return _erro("Empresa não encontrada", 404)

    try:
        db.session.delete(empresa)
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        return _erro(
            "Não foi possível remover a empresa. "
            "Verifique se existem registros vinculados.",
            409,
        )

    return "", 204

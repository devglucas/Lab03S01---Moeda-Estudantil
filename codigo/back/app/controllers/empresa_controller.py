
"""Controller das empresas parceiras: CRUD em /api/empresas."""
from flask import Blueprint, jsonify, request
from sqlalchemy.exc import IntegrityError

from app.extensions import db
from app.models.empresa import EmpresaParceira
from app.models.usuario import Usuario
from app.validacao import email_valido, faltantes, texto
# Precisa tirar isso de validacao, preferi deixar sem, se quiser da p voltar tbm, aluno e instituicao ja ta sem
empresa_bp = Blueprint("empresas", __name__, url_prefix="/api/empresas")


def _erro(mensagem, status, campos=None):
    corpo = {"erro": mensagem}
    if campos:
        corpo["campos"] = campos
    return jsonify(corpo), status

def _buscar(empresa_id):
    return db.session.get(EmpresaParceira, empresa_id)

@empresa_bp.post("")
def criar():
    dados = request.get_json(silent=True) or {}

    campos = faltantes(dados, ["nome", "email", "login", "senha"])



    senha = dados.get("senha")
    if "senha" not in campos and (
        not isinstance(senha, str) or len(senha) < 6
    ):
        campos["senha"] = "A senha deve ter no mínimo 6 caracteres"

    if campos:
        return _erro("Dados inválidos", 400, campos)

    login = texto(dados, "login")
    email = texto(dados, "email")

    if Usuario.query.filter_by(login=login).first():
        return _erro("Login já cadastrado", 409)

    if EmpresaParceira.query.filter_by(email=email).first():
        return _erro("E-mail já cadastrado", 409)

    empresa = EmpresaParceira(
        login=login,
        nome=texto(dados, "nome"),
        email=email,
    )
    empresa.definir_senha(senha)

    db.session.add(empresa)

    try:
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        return _erro("Login ou e-mail já cadastrado", 409)

    return jsonify(empresa.to_dict()), 201


# READ - listar todas
@empresa_bp.get("")
def listar():
    empresas = EmpresaParceira.query.order_by(
        EmpresaParceira.nome
    ).all()

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

    dados = request.get_json(silent=True) or {}
    campos = faltantes(dados, ["nome", "email"])

    if "email" not in campos and not email_valido(texto(dados, "email")):
        campos["email"] = "E-mail inválido"

    senha = dados.get("senha")
    if senha is not None and senha != "":
        if not isinstance(senha, str) or len(senha) < 6:
            campos["senha"] = "A senha deve ter no mínimo 6 caracteres"

    if campos:
        return _erro("Dados inválidos", 400, campos)

    email = texto(dados, "email")

    outra = EmpresaParceira.query.filter(
        EmpresaParceira.email == email,
        EmpresaParceira.id != empresa_id,
    ).first()

    if outra:
        return _erro("E-mail já cadastrado", 409)

    empresa.nome = texto(dados, "nome")
    empresa.email = email

    if senha:
        empresa.definir_senha(senha)

    try:
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        return _erro("E-mail já cadastrado", 409)

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

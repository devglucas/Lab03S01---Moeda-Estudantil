
"""Controller dos alunos: CRUD em /api/usuarios."""
from flask import Blueprint, jsonify, request
from sqlalchemy.exc import IntegrityError

from app.extensions import db
from app.models.aluno import Aluno
from app.models.usuario import Usuario
from app.models.instituicao import InstituicaoEnsino


aluno_bp = Blueprint("aluno", __name__, url_prefix="/api/aluno")


def _erro(mensagem, status, campos=None):
    corpo = {"erro": mensagem}
    if campos:
        corpo["campos"] = campos
    return jsonify(corpo), status


def buscar(aluno_id):
    return db.session.get(Aluno, aluno_id)


@aluno_bp.post("")
def criar():
    dados = request.get_json(silent=True)
    if not isinstance(dados, dict):
        return _erro("Envie os dados em JSON.", 400)

    obrigatorios = [
        "nome", "email", "cpf", "rg", "endereco",
        "curso", "instituicaoId", "login", "senha"
    ]

    login = dados.get("login")
    email = dados.get("email")
    cpf = dados.get("cpf")

    if Usuario.query.filter_by(login=login).first():
        return _erro("Login já cadastrado", 409)

    if Aluno.query.filter_by(email=email).first():
        return _erro("E-mail já cadastrado", 409)

    if Aluno.query.filter_by(cpf=cpf).first():
        return _erro("CPF já cadastrado", 409)

    instituicao = db.session.get(
        InstituicaoEnsino, dados["instituicaoId"]
    )

    if instituicao is None:
        return _erro("Instituição de ensino não encontrada", 404)

    aluno = Aluno(
        login=login,
        tipo="aluno",
        nome=texto(dados, "nome"),
        email=email,
        cpf=cpf,
        rg=texto(dados, "rg"),
        endereco=texto(dados, "endereco"),
        curso=texto(dados, "curso"),
        instituicao_id=instituicao.id,
        saldo=0,
    )

    aluno.definir_senha(dados["senha"])
    db.session.add(aluno)

    try:
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        return _erro("Login, e-mail ou CPF já cadastrado", 409)

    return jsonify(aluno.to_dict()), 201

@aluno_bp.get("")
def listar():
    alunos = Aluno.query.order_by(Aluno.nome).all()
    return jsonify([aluno.to_dict() for aluno in alunos])

@aluno_bp.get("/<int:aluno_id>")
def buscar(aluno_id):
    aluno = buscar(aluno_id)

    if aluno is None:
        return _erro("Aluno não encontrado", 404)

    return jsonify(aluno.to_dict())

@aluno_bp.put("/<int:aluno_id>")
def atualizar(aluno_id):
    aluno = buscar(aluno_id)

    if aluno is None:
        return _erro("Aluno não encontrado", 404)

    dados = request.get_json(silent=True)
    if not isinstance(dados, dict):
        return _erro("Envie os dados em JSON.", 400)

    email = texto(dados, "email").lower()
    cpf = texto(dados, "cpf")

    outro_email = Aluno.query.filter(
        Aluno.email == email,
        Aluno.id != aluno_id
    ).first()

    if outro_email:
        return _erro("E-mail já cadastrado", 409)

    outro_cpf = Aluno.query.filter(
        Aluno.cpf == cpf,
        Aluno.id != aluno_id
    ).first()

    if outro_cpf:
        return _erro("CPF já cadastrado", 409)

    instituicao = db.session.get(
        InstituicaoEnsino, dados["instituicaoId"]
    )

    if instituicao is None:
        return _erro("Instituição de ensino não encontrada", 404)

    aluno.nome = texto(dados, "nome")
    aluno.email = email
    aluno.cpf = cpf
    aluno.rg = texto(dados, "rg")
    aluno.endereco = texto(dados, "endereco")
    aluno.curso = texto(dados, "curso")
    aluno.instituicao_id = instituicao.id

    senha = dados.get("senha")
    if senha:
        if not isinstance(senha, str) or len(senha) < 6:
            return _erro(
                "Dados inválidos", 400,
                {"senha": "A senha deve ter no mínimo 6 caracteres"}
            )
        aluno.definir_senha(senha)

    try:
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        return _erro("E-mail ou CPF já cadastrado", 409)

    return jsonify(aluno.to_dict())

@aluno_bp.delete("/<int:aluno_id>")
def remover(aluno_id):
    aluno = buscar(aluno_id)

    if aluno is None:
        return _erro("Aluno não encontrado", 404)

    try:
        db.session.delete(aluno)
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        return _erro(
            "Não foi possível remover o aluno. "
            "Verifique se existem registros vinculados.",
            409
        )

    return "", 204

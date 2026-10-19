"""Controller dos alunos: CRUD em /api/alunos."""
from flask import Blueprint, jsonify, request
from sqlalchemy.exc import IntegrityError

from app.extensions import db
from app.models.aluno import Aluno
from app.models.instituicao import InstituicaoEnsino
from app.models.usuario import Usuario
from app.validacao import (
    apenas_digitos,
    email_valido,
    faltantes,
    senha_valida,
    texto,
)


aluno_bp = Blueprint("alunos", __name__, url_prefix="/api/alunos")

CAMPOS_ALUNO = ["nome", "email", "cpf", "rg", "endereco", "curso", "instituicaoId"]


def _erro(mensagem, status, campos=None):
    corpo = {"erro": mensagem}
    if campos:
        corpo["campos"] = campos
    return jsonify(corpo), status


def _buscar(aluno_id):
    return db.session.get(Aluno, aluno_id)


def _validar(dados, obrigatorios):
    """Valida o corpo da requisição e devolve (campos_invalidos, instituicao)."""
    campos = faltantes(dados, obrigatorios)

    if "email" not in campos and not email_valido(texto(dados, "email")):
        campos["email"] = "E-mail inválido"

    if "cpf" not in campos and len(apenas_digitos(texto(dados, "cpf"))) != 11:
        campos["cpf"] = "O CPF deve ter 11 dígitos"

    # Na criação a senha é obrigatória; na edição só é validada se vier preenchida.
    senha = dados.get("senha")
    if "senha" not in campos and senha not in (None, "") and not senha_valida(senha):
        campos["senha"] = "A senha deve ter no mínimo 6 caracteres"

    instituicao = None
    if "instituicaoId" not in campos:
        try:
            instituicao = db.session.get(InstituicaoEnsino, int(dados["instituicaoId"]))
        except (TypeError, ValueError):
            instituicao = None
        if instituicao is None:
            campos["instituicaoId"] = "Instituição de ensino não encontrada"

    return campos, instituicao


@aluno_bp.post("")
def criar():
    dados = request.get_json(silent=True)
    if not isinstance(dados, dict):
        return _erro("Envie os dados em JSON.", 400)

    campos, instituicao = _validar(dados, CAMPOS_ALUNO + ["senha"])
    if campos:
        return _erro("Dados inválidos", 400, campos)

    email = texto(dados, "email").lower()
    cpf = apenas_digitos(texto(dados, "cpf"))

    # O e-mail é o login, então não pode se repetir em nenhum perfil.
    if Usuario.query.filter_by(login=email).first():
        return _erro("E-mail já cadastrado", 409)

    if Aluno.query.filter_by(cpf=cpf).first():
        return _erro("CPF já cadastrado", 409)

    aluno = Aluno(
        login=email,
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
        return _erro("E-mail ou CPF já cadastrado", 409)

    return jsonify(aluno.to_dict()), 201


@aluno_bp.get("")
def listar():
    alunos = Aluno.query.order_by(Aluno.nome).all()
    return jsonify([aluno.to_dict() for aluno in alunos])


@aluno_bp.get("/<int:aluno_id>")
def buscar(aluno_id):
    aluno = _buscar(aluno_id)

    if aluno is None:
        return _erro("Aluno não encontrado", 404)

    return jsonify(aluno.to_dict())


@aluno_bp.put("/<int:aluno_id>")
def atualizar(aluno_id):
    aluno = _buscar(aluno_id)

    if aluno is None:
        return _erro("Aluno não encontrado", 404)

    dados = request.get_json(silent=True)
    if not isinstance(dados, dict):
        return _erro("Envie os dados em JSON.", 400)

    campos, instituicao = _validar(dados, CAMPOS_ALUNO)
    if campos:
        return _erro("Dados inválidos", 400, campos)

    email = texto(dados, "email").lower()
    cpf = apenas_digitos(texto(dados, "cpf"))

    outro_email = Usuario.query.filter(
        Usuario.login == email,
        Usuario.id != aluno_id,
    ).first()

    if outro_email:
        return _erro("E-mail já cadastrado", 409)

    outro_cpf = Aluno.query.filter(
        Aluno.cpf == cpf,
        Aluno.id != aluno_id,
    ).first()

    if outro_cpf:
        return _erro("CPF já cadastrado", 409)

    aluno.nome = texto(dados, "nome")
    aluno.email = email
    aluno.login = email
    aluno.cpf = cpf
    aluno.rg = texto(dados, "rg")
    aluno.endereco = texto(dados, "endereco")
    aluno.curso = texto(dados, "curso")
    aluno.instituicao_id = instituicao.id

    # Senha é opcional na edição: só troca se vier preenchida.
    senha = dados.get("senha")
    if senha:
        aluno.definir_senha(senha)

    try:
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        return _erro("E-mail ou CPF já cadastrado", 409)

    return jsonify(aluno.to_dict())


@aluno_bp.delete("/<int:aluno_id>")
def remover(aluno_id):
    aluno = _buscar(aluno_id)

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
            409,
        )

    return "", 204

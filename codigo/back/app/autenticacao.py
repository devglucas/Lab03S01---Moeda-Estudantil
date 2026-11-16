"""Autenticação simples por token (JWT) e controle de acesso por perfil.

O login devolve um token assinado com o id e o tipo do usuário. As rotas
protegidas leem o token do header ``Authorization: Bearer <token>`` e deixam o
usuário autenticado em ``flask.g.usuario``.
"""
from datetime import datetime, timedelta, timezone
from functools import wraps

import jwt
from flask import current_app, g, request

from app.repositories import UsuarioRepository
from app.services.erros import AcessoNegado, NaoAutenticado

VALIDADE_TOKEN = timedelta(hours=8)
ALGORITMO = "HS256"


def gerar_token(usuario):
    agora = datetime.now(timezone.utc)
    dados = {
        "sub": str(usuario.id),
        "tipo": usuario.tipo,
        "iat": agora,
        "exp": agora + VALIDADE_TOKEN,
    }
    return jwt.encode(dados, current_app.config["SECRET_KEY"], algorithm=ALGORITMO)


def usuario_do_token():
    cabecalho = request.headers.get("Authorization", "")
    tipo, _, token = cabecalho.partition(" ")
    if tipo != "Bearer" or not token:
        raise NaoAutenticado("Faça login para continuar.")

    try:
        dados = jwt.decode(token, current_app.config["SECRET_KEY"], algorithms=[ALGORITMO])
        usuario = UsuarioRepository().buscar_por_id(int(dados["sub"]))
    except (jwt.InvalidTokenError, KeyError, ValueError):
        usuario = None

    if usuario is None:
        raise NaoAutenticado("Sessão expirada. Faça login novamente.")
    return usuario


def exige_perfil(*perfis):
    """Exige um usuário logado; com ``perfis``, só aceita esses tipos."""

    def decorador(view):
        @wraps(view)
        def protegida(*args, **kwargs):
            g.usuario = usuario_do_token()
            if perfis and g.usuario.tipo not in perfis:
                raise AcessoNegado("Seu perfil não tem acesso a esta funcionalidade.")
            return view(*args, **kwargs)

        return protegida

    return decorador

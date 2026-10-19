"""Funções de validação compartilhadas pelos controllers."""
import re

EMAIL_REGEX = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


def texto(dados, campo):
    """Lê um campo de texto do JSON já sem espaços nas pontas ("" se ausente)."""
    valor = dados.get(campo)
    if valor is None:
        return ""
    return str(valor).strip()


def apenas_digitos(valor):
    return re.sub(r"\D", "", valor or "")


def faltantes(dados, obrigatorios):
    """Devolve {campo: mensagem} para cada campo obrigatório vazio ou ausente."""
    return {
        campo: "Campo obrigatório"
        for campo in obrigatorios
        if dados.get(campo) is None or texto(dados, campo) == ""
    }


def email_valido(email):
    return bool(EMAIL_REGEX.match(email or ""))


def senha_valida(senha):
    return isinstance(senha, str) and len(senha) >= 6

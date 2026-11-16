"""Regras do login: confere e-mail e senha e emite o token de sessão."""
from app.autenticacao import gerar_token
from app.repositories import UsuarioRepository
from app.services.erros import DadosInvalidos, NaoAutenticado, exigir_json
from app.validacao import texto


class AuthService:
    def __init__(self, usuarios=None):
        self.usuarios = usuarios or UsuarioRepository()

    def entrar(self, dados):
        dados = exigir_json(dados)
        email = texto(dados, "email").lower()
        senha = dados.get("senha")

        campos = {}
        if not email:
            campos["email"] = "Informe o e-mail"
        if not isinstance(senha, str) or not senha:
            campos["senha"] = "Informe a senha"
        if campos:
            raise DadosInvalidos("Dados inválidos", campos)

        usuario = self.usuarios.buscar_por_login(email)
        # A mesma mensagem nos dois casos para não revelar quais e-mails existem.
        if usuario is None or not usuario.verificar_senha(senha):
            raise NaoAutenticado("E-mail ou senha incorretos.")

        return {"token": gerar_token(usuario), "usuario": perfil_json(usuario)}


def perfil_json(usuario):
    """Dados do perfil logado, com o tipo para o front escolher as abas."""
    return {**usuario.to_dict(), "tipo": usuario.tipo}

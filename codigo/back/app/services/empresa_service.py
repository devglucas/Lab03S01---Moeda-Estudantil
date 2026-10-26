"""Regras de negócio das empresas parceiras."""
from app.models.empresa import EmpresaParceira
from app.repositories import EmpresaRepository, ErroIntegridade, UsuarioRepository
from app.services.erros import Conflito, DadosInvalidos, NaoEncontrado, exigir_json
from app.validacao import apenas_digitos, email_valido, faltantes, senha_valida, texto

CAMPOS_EMPRESA = ["nome", "email", "cnpj"]


class EmpresaService:
    def __init__(self, empresas=None, usuarios=None):
        self.empresas = empresas or EmpresaRepository()
        self.usuarios = usuarios or UsuarioRepository()

    def listar(self):
        return self.empresas.listar()

    def buscar(self, empresa_id):
        empresa = self.empresas.buscar_por_id(empresa_id)
        if empresa is None:
            raise NaoEncontrado("Empresa não encontrada")
        return empresa

    def criar(self, dados):
        dados = exigir_json(dados)
        self._validar(dados, CAMPOS_EMPRESA + ["senha"])

        email = texto(dados, "email").lower()
        cnpj = apenas_digitos(texto(dados, "cnpj"))
        self._verificar_unicos(email, cnpj)

        empresa = EmpresaParceira(
            login=email,
            nome=texto(dados, "nome"),
            email=email,
            cnpj=cnpj,
        )
        empresa.definir_senha(dados["senha"])
        return self._salvar(empresa)

    def atualizar(self, empresa_id, dados):
        empresa = self.buscar(empresa_id)
        dados = exigir_json(dados)
        self._validar(dados, CAMPOS_EMPRESA)

        email = texto(dados, "email").lower()
        cnpj = apenas_digitos(texto(dados, "cnpj"))
        self._verificar_unicos(email, cnpj, empresa_id)

        empresa.nome = texto(dados, "nome")
        empresa.email = email
        empresa.login = email
        empresa.cnpj = cnpj

        senha = dados.get("senha")
        if senha:
            empresa.definir_senha(senha)

        return self._salvar(empresa)

    def remover(self, empresa_id):
        empresa = self.buscar(empresa_id)
        try:
            self.empresas.remover(empresa)
        except ErroIntegridade:
            raise Conflito(
                "Não foi possível remover a empresa. "
                "Verifique se existem registros vinculados."
            )

    def _validar(self, dados, obrigatorios):
        campos = faltantes(dados, obrigatorios)

        if "email" not in campos and not email_valido(texto(dados, "email")):
            campos["email"] = "E-mail inválido"

        if "cnpj" not in campos and len(apenas_digitos(texto(dados, "cnpj"))) != 14:
            campos["cnpj"] = "O CNPJ deve ter 14 dígitos"

        # Na criação a senha é obrigatória; na edição só é validada se vier preenchida.
        senha = dados.get("senha")
        if "senha" not in campos and senha not in (None, "") and not senha_valida(senha):
            campos["senha"] = "A senha deve ter no mínimo 6 caracteres"

        if campos:
            raise DadosInvalidos("Dados inválidos", campos)

    def _verificar_unicos(self, email, cnpj, empresa_id=None):
        # O e-mail é o login, então não pode se repetir em nenhum perfil.
        if self.usuarios.login_em_uso(email, empresa_id):
            raise Conflito("E-mail já cadastrado")
        if self.empresas.cnpj_em_uso(cnpj, empresa_id):
            raise Conflito("CNPJ já cadastrado")

    def _salvar(self, empresa):
        try:
            return self.empresas.salvar(empresa)
        except ErroIntegridade:
            raise Conflito("E-mail ou CNPJ já cadastrado")

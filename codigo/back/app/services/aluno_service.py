"""Regras de negócio dos alunos (cadastro, edição e exclusão)."""
from app.models.aluno import Aluno
from app.repositories import (
    AlunoRepository,
    ErroIntegridade,
    InstituicaoRepository,
    UsuarioRepository,
)
from app.services.erros import Conflito, DadosInvalidos, NaoEncontrado, exigir_json
from app.validacao import apenas_digitos, email_valido, faltantes, senha_valida, texto

CAMPOS_ALUNO = ["nome", "email", "cpf", "rg", "endereco", "curso", "instituicaoId"]


class AlunoService:
    def __init__(self, alunos=None, usuarios=None, instituicoes=None):
        self.alunos = alunos or AlunoRepository()
        self.usuarios = usuarios or UsuarioRepository()
        self.instituicoes = instituicoes or InstituicaoRepository()

    def listar(self):
        return self.alunos.listar()

    def buscar(self, aluno_id):
        aluno = self.alunos.buscar_por_id(aluno_id)
        if aluno is None:
            raise NaoEncontrado("Aluno não encontrado")
        return aluno

    def criar(self, dados):
        dados = exigir_json(dados)
        instituicao = self._validar(dados, CAMPOS_ALUNO + ["senha"])

        email = texto(dados, "email").lower()
        cpf = apenas_digitos(texto(dados, "cpf"))
        self._verificar_unicos(email, cpf)

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
        return self._salvar(aluno)

    def atualizar(self, aluno_id, dados):
        aluno = self.buscar(aluno_id)
        dados = exigir_json(dados)
        instituicao = self._validar(dados, CAMPOS_ALUNO)

        email = texto(dados, "email").lower()
        cpf = apenas_digitos(texto(dados, "cpf"))
        self._verificar_unicos(email, cpf, aluno_id)

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

        return self._salvar(aluno)

    def remover(self, aluno_id):
        aluno = self.buscar(aluno_id)
        try:
            self.alunos.remover(aluno)
        except ErroIntegridade:
            raise Conflito(
                "Não foi possível remover o aluno. "
                "Verifique se existem registros vinculados."
            )

    def _validar(self, dados, obrigatorios):
        """Valida o corpo da requisição e devolve a instituição escolhida."""
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
                instituicao = self.instituicoes.buscar_por_id(int(dados["instituicaoId"]))
            except (TypeError, ValueError):
                instituicao = None
            if instituicao is None:
                campos["instituicaoId"] = "Instituição de ensino não encontrada"

        if campos:
            raise DadosInvalidos("Dados inválidos", campos)
        return instituicao

    def _verificar_unicos(self, email, cpf, aluno_id=None):
        # O e-mail é o login, então não pode se repetir em nenhum perfil.
        if self.usuarios.login_em_uso(email, aluno_id):
            raise Conflito("E-mail já cadastrado")
        if self.alunos.cpf_em_uso(cpf, aluno_id):
            raise Conflito("CPF já cadastrado")

    def _salvar(self, aluno):
        try:
            return self.alunos.salvar(aluno)
        except ErroIntegridade:
            raise Conflito("E-mail ou CPF já cadastrado")

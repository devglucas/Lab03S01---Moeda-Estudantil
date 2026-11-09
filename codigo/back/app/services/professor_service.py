"""Regras de negócio dos alunos (cadastro, edição e exclusão)."""
from app.models.professor import Professor
from app.repositories import (
    ProfessorRepository,
    ErroIntegridade,
    InstituicaoRepository,
    UsuarioRepository,
)
from app.services.erros import Conflito, DadosInvalidos, NaoEncontrado, exigir_json
from app.validacao import apenas_digitos, email_valido, faltantes, senha_valida, texto

CAMPOS_PROFESSOR = ["nome", "email", "cpf", "departamento", "instituicaoId"]


class ProfessorService:
    def __init__(self, professores=None, usuarios=None, instituicoes=None):
        self.professor = professores or ProfessorRepository()
        self.usuarios = usuarios or UsuarioRepository()
        self.instituicoes = instituicoes or InstituicaoRepository()

    def listar(self):
        return self.professor.listar()

    def buscar(self, professor_id):
        professor = self.professor.buscar_por_id(professor_id)
        if professor is None:
            raise NaoEncontrado("Professor não encontrado")
        return professor

    def criar(self, dados):
        dados = exigir_json(dados)
        instituicao = self._validar(dados, CAMPOS_PROFESSOR + ["senha"])

        email = texto(dados, "email").lower()
        cpf = apenas_digitos(texto(dados, "cpf"))
        self._verificar_unicos(email, cpf)

        professor = Professor(
            login=email,
            nome=texto(dados, "nome"),
            email=email,
            cpf=cpf,
            departamento=texto(dados, "departamento"),
            instituicao_id=instituicao.id,
            saldo=0,
        )
        professor.definir_senha(dados["senha"])
        # Decisão do grupo: o professor já nasce com as moedas do semestre.
        professor.receber_moedas_semestre()
        return self._salvar(professor)

    # def atualizar(self, aluno_id, dados):
    #     aluno = self.buscar(aluno_id)
    #     dados = exigir_json(dados)
    #     instituicao = self._validar(dados, CAMPOS_ALUNO)

    #     email = texto(dados, "email").lower()
    #     cpf = apenas_digitos(texto(dados, "cpf"))
    #     self._verificar_unicos(email, cpf, aluno_id)

    #     aluno.nome = texto(dados, "nome")
    #     aluno.email = email
    #     aluno.login = email
    #     aluno.cpf = cpf
    #     aluno.rg = texto(dados, "rg")
    #     aluno.endereco = texto(dados, "endereco")
    #     aluno.curso = texto(dados, "curso")
    #     aluno.instituicao_id = instituicao.id

    #     # Senha é opcional na edição: só troca se vier preenchida.
    #     senha = dados.get("senha")
    #     if senha:
    #         aluno.definir_senha(senha)

    #     return self._salvar(aluno)

    # def remover(self, aluno_id):
    #     aluno = self.buscar(aluno_id)
    #     try:
    #         self.alunos.remover(aluno)
    #     except ErroIntegridade:
    #         raise Conflito(
    #             "Não foi possível remover o aluno. "
    #             "Verifique se existem registros vinculados."
    #         )

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

    def _verificar_unicos(self, email, cpf, professor_id=None):
        # O e-mail é o login, então não pode se repetir em nenhum perfil.
        if self.usuarios.login_em_uso(email, professor_id):
            raise Conflito("E-mail já cadastrado")
        if self.professor.cpf_em_uso(cpf, professor_id):
            raise Conflito("CPF já cadastrado")

    def _salvar(self, aluno):
        try:
            return self.professor.salvar(aluno)
        except ErroIntegridade:
            raise Conflito("E-mail ou CPF já cadastrado")

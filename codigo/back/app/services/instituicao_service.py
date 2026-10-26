"""Regras de negócio das instituições de ensino."""
from app.models.instituicao import InstituicaoEnsino
from app.repositories import AlunoRepository, ErroIntegridade, InstituicaoRepository
from app.services.erros import Conflito, DadosInvalidos, NaoEncontrado, exigir_json


class InstituicaoService:
    def __init__(self, instituicoes=None, alunos=None):
        self.instituicoes = instituicoes or InstituicaoRepository()
        self.alunos = alunos or AlunoRepository()

    def listar(self):
        return self.instituicoes.listar()

    def buscar(self, instituicao_id):
        instituicao = self.instituicoes.buscar_por_id(instituicao_id)
        if instituicao is None:
            raise NaoEncontrado("Instituição não encontrada")
        return instituicao

    def criar(self, dados):
        nome = self._validar_nome(dados)

        if self.instituicoes.nome_em_uso(nome):
            raise Conflito("Instituição já cadastrada")

        try:
            return self.instituicoes.salvar(InstituicaoEnsino(nome=nome))
        except ErroIntegridade:
            raise Conflito("Instituição já cadastrada")

    def atualizar(self, instituicao_id, dados):
        instituicao = self.buscar(instituicao_id)
        nome = self._validar_nome(dados)

        if self.instituicoes.nome_em_uso(nome, instituicao_id):
            raise Conflito("Já existe uma instituição com esse nome")

        instituicao.nome = nome
        try:
            return self.instituicoes.salvar(instituicao)
        except ErroIntegridade:
            raise Conflito("Já existe uma instituição com esse nome")

    def remover(self, instituicao_id):
        instituicao = self.buscar(instituicao_id)

        # Impede excluir instituições vinculadas a alunos.
        if self.alunos.existe_na_instituicao(instituicao_id):
            raise Conflito(
                "Não é possível remover uma instituição que possui alunos vinculados."
            )

        try:
            self.instituicoes.remover(instituicao)
        except ErroIntegridade:
            raise Conflito("Não foi possível remover a instituição.")

    def _validar_nome(self, dados):
        try:
            exigir_json(dados)
        except DadosInvalidos:
            raise DadosInvalidos("Dados inválidos", {"nome": "Envie os dados em JSON."})

        nome = dados.get("nome")

        if not isinstance(nome, str) or not nome.strip():
            raise DadosInvalidos("Dados inválidos", {"nome": "O nome é obrigatório."})

        nome = nome.strip()

        if len(nome) > 160:
            raise DadosInvalidos(
                "Dados inválidos", {"nome": "O nome deve ter até 160 caracteres."}
            )

        return nome

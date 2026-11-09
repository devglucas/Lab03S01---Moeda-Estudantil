"""Regras de negócio das transações: envio de moedas e extrato."""
from app.models.transacao import EnvioMoeda
from app.repositories import (
    AlunoRepository,
    ErroIntegridade,
    ProfessorRepository,
    TransacaoRepository,
)
from app.services.email_service import EmailService
from app.services.erros import Conflito, DadosInvalidos, NaoEncontrado, exigir_json

TAMANHO_MAXIMO_MENSAGEM = 500


class TransacaoService:
    def __init__(self, transacoes=None, professores=None, alunos=None, email_service=None):
        self.transacoes = transacoes or TransacaoRepository()
        self.professores = professores or ProfessorRepository()
        self.alunos = alunos or AlunoRepository()
        self.email_service = email_service or EmailService()

    def listar_todas(self):
        return self.transacoes.listar_todas()

    def enviar_moedas(self, dados):
        dados = exigir_json(dados)
        mensagem = self._validar_envio(dados)

        professor = self._buscar_professor(dados["professorId"])
        aluno = self._buscar_aluno(dados["alunoId"])
        valor = dados["valor"]

        if professor.instituicao_id != aluno.instituicao_id:
            raise DadosInvalidos(
                "Dados inválidos",
                {"alunoId": "O aluno é de outra instituição de ensino"},
            )
        if valor > professor.saldo:
            raise DadosInvalidos(
                f"Saldo insuficiente: o professor tem {professor.saldo} moeda(s).",
                {"valor": "Valor maior que o saldo do professor"},
            )

        professor.debitar(valor)
        aluno.receber_moedas(valor)
        envio = EnvioMoeda(professor=professor, aluno=aluno, valor=valor, mensagem=mensagem)

        # O débito, o crédito e o registro vão no mesmo commit: ou tudo é
        # gravado, ou nada é.
        try:
            self.transacoes.registrar(envio, professor, aluno)
        except ErroIntegridade:
            raise Conflito("Não foi possível registrar o envio de moedas.")

        self._notificar_aluno(aluno, professor, envio)
        return envio

    def extrato_professor(self, professor_id):
        professor = self._buscar_professor(professor_id)
        return {
            "saldo": professor.saldo,
            "transacoes": self.transacoes.listar_por_professor(professor_id),
        }

    def extrato_aluno(self, aluno_id):
        aluno = self._buscar_aluno(aluno_id)
        return {
            "saldo": aluno.saldo,
            "transacoes": self.transacoes.listar_por_aluno(aluno_id),
        }

    def _validar_envio(self, dados):
        """Valida o corpo da requisição e devolve o motivo já sem espaços."""
        campos = {}

        if not _inteiro_positivo(dados.get("professorId")):
            campos["professorId"] = "Selecione o professor"
        if not _inteiro_positivo(dados.get("alunoId")):
            campos["alunoId"] = "Selecione o aluno"
        if not _inteiro_positivo(dados.get("valor")):
            campos["valor"] = "Informe um número inteiro maior que zero"

        mensagem = dados.get("mensagem")
        mensagem = mensagem.strip() if isinstance(mensagem, str) else ""
        if not mensagem:
            campos["mensagem"] = "O motivo do reconhecimento é obrigatório"
        elif len(mensagem) > TAMANHO_MAXIMO_MENSAGEM:
            campos["mensagem"] = f"O motivo deve ter até {TAMANHO_MAXIMO_MENSAGEM} caracteres"

        if campos:
            raise DadosInvalidos("Dados inválidos", campos)
        return mensagem

    def _buscar_professor(self, professor_id):
        professor = self.professores.buscar_por_id(professor_id)
        if professor is None:
            raise NaoEncontrado("Professor não encontrado")
        return professor

    def _buscar_aluno(self, aluno_id):
        aluno = self.alunos.buscar_por_id(aluno_id)
        if aluno is None:
            raise NaoEncontrado("Aluno não encontrado")
        return aluno

    def _notificar_aluno(self, aluno, professor, transacao):
        corpo = (
            f"Olá, {aluno.nome}!\n\n"
            f"O professor {professor.nome} enviou {transacao.valor} moeda(s) para você.\n"
            f"Motivo: {transacao.mensagem}\n\n"
            f"Seu saldo atual é de {aluno.saldo} moeda(s)."
        )
        self.email_service.enviar(aluno.email, "Você recebeu moedas!", corpo)


def _inteiro_positivo(valor):
    return isinstance(valor, int) and not isinstance(valor, bool) and valor > 0

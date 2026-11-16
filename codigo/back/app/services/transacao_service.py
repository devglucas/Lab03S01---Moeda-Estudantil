"""Regras de negócio das transações: envio de moedas e extrato."""
from app.models.transacao import EnvioMoeda
from app.repositories import AlunoRepository, ErroIntegridade, TransacaoRepository
from app.services.erros import Conflito, DadosInvalidos, NaoEncontrado, exigir_json
from app.services.notificacao_service import NotificacaoService

TAMANHO_MAXIMO_MENSAGEM = 500


class TransacaoService:
    def __init__(self, transacoes=None, alunos=None, notificacoes=None):
        self.transacoes = transacoes or TransacaoRepository()
        self.alunos = alunos or AlunoRepository()
        self.notificacoes = notificacoes or NotificacaoService()

    def enviar_moedas(self, professor, dados):
        """``professor`` é o usuário logado; os dados trazem aluno, valor e motivo."""
        dados = exigir_json(dados)
        mensagem = self._validar_envio(dados)

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

        self.notificacoes.notificar_envio_moedas(envio)
        return envio

    def extrato(self, usuario):
        """Extrato do usuário logado: envios do professor ou movimentações do aluno."""
        if usuario.tipo == "professor":
            transacoes = self.transacoes.listar_por_professor(usuario.id)
        else:
            transacoes = self.transacoes.listar_por_aluno(usuario.id)
        return {"saldo": usuario.saldo, "transacoes": transacoes}

    def _validar_envio(self, dados):
        """Valida o corpo da requisição e devolve o motivo já sem espaços."""
        campos = {}

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

    def _buscar_aluno(self, aluno_id):
        aluno = self.alunos.buscar_por_id(aluno_id)
        if aluno is None:
            raise NaoEncontrado("Aluno não encontrado")
        return aluno


def _inteiro_positivo(valor):
    return isinstance(valor, int) and not isinstance(valor, bool) and valor > 0

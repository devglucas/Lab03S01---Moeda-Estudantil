from app.extensions import db
from app.models.aluno import Aluno
from app.models.professor import Professor
from app.models.transacao import Transacao
from app.repositories.transacao_repository import TransacaoRepository
from app.services.email_service import EmailService
# from app.services.professor_service import NaoEncontradoError, ValidacaoError
from app.services.erros import Conflito, DadosInvalidos, NaoEncontrado, exigir_json

class TransacaoService:
    def __init__(self, repository=None, email_service=None):
        self.repository = repository or TransacaoRepository()
        self.email_service = email_service or EmailService()

    # ---------- R08: enviar moedas ----------
    def enviar_moedas(self, dados):
        professor_id = dados.get("professorId")
        aluno_id = dados.get("alunoId")
        valor = dados.get("valor")
        mensagem = (dados.get("mensagem") or "").strip()

        if not professor_id or not aluno_id:
            raise DadosInvalidos("Professor e aluno são obrigatórios")
        if isinstance(valor, bool) or not isinstance(valor, int) or valor <= 0:
            raise DadosInvalidos("Valor deve ser um número inteiro maior que zero")
        if not mensagem:
            raise DadosInvalidos("A mensagem de reconhecimento é obrigatória")
        if len(mensagem) > 500:
            raise DadosInvalidos("A mensagem deve ter no máximo 500 caracteres")

        professor = db.session.get(Professor, professor_id)
        if not professor:
            raise NaoEncontrado("Professor não encontrado")
        aluno = db.session.get(Aluno, aluno_id)
        if not aluno:
            raise NaoEncontrado("Aluno não encontrado")
        if professor.instituicao_id != aluno.instituicao_id:
            raise NaoEncontrado("Professor e aluno são de instituições diferentes")

        # R09: verifica saldo (debitar lança ValueError se insuficiente)
        try:
            professor.debitar(valor)
        except ValueError as e:
            raise DadosInvalidos(str(e))
        aluno.saldo += valor

        transacao = Transacao(
            professor_id=professor.id, aluno_id=aluno.id, valor=valor, mensagem=mensagem
        )
        self.repository.registrar(transacao, professor, aluno)

        self._notificar_aluno(aluno, professor, transacao)
        return transacao

    def _notificar_aluno(self, aluno, professor, transacao):
        corpo = (
            f"Olá, {aluno.nome}!\n\n"
            f"O professor {professor.nome} enviou {transacao.valor} moeda(s) para você.\n"
            f"Motivo: {transacao.mensagem}\n\n"
            f"Seu saldo atual é de {aluno.saldo} moeda(s)."
        )
        self.email_service.enviar(aluno.email, "Você recebeu moedas!", corpo)

    # ---------- R11: extrato ----------
    def extrato_professor(self, professor_id):
        professor = db.session.get(Professor, professor_id)
        if not professor:
            raise NaoEncontrado("Professor não encontrado")
        return {
            "saldo": professor.saldo,
            "transacoes": self.repository.listar_por_professor(professor_id),
        }

    def extrato_aluno(self, aluno_id):
        aluno = db.session.get(Aluno, aluno_id)
        if not aluno:
            raise NaoEncontrado("Aluno não encontrado")
        return {
            "saldo": aluno.saldo,
            "transacoes": self.repository.listar_por_aluno(aluno_id),
        }

    def recebe1000(self, professor_id):
        professor = db.session.get(Professor, professor_id)
        if not professor:
            raise NaoEncontrado("Professor não encontrado")

        professor.receber_moedas_semestre()  # saldo += 1000
        self.repository.salvar(professor)
        return professor
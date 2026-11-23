"""Regras da troca de moedas por vantagem: saldo, cupom e notificações."""
import secrets

from app.models.transacao import TrocaVantagem
from app.repositories import ErroIntegridade, TransacaoRepository, VantagemRepository
from app.services.erros import Conflito, DadosInvalidos, NaoEncontrado, exigir_json
from app.services.notificacao_service import NotificacaoService

# Sem 0/O e 1/I/L, que se confundem na hora de ditar ou digitar o código.
ALFABETO_CODIGO = "ABCDEFGHJKMNPQRSTUVWXYZ23456789"
TAMANHO_CODIGO = 8
TENTATIVAS_CODIGO = 5


class TrocaService:
    def __init__(self, transacoes=None, vantagens=None, notificacoes=None):
        self.transacoes = transacoes or TransacaoRepository()
        self.vantagens = vantagens or VantagemRepository()
        self.notificacoes = notificacoes or NotificacaoService()

    def trocar(self, aluno, dados):
        """``aluno`` é o usuário logado; os dados trazem a vantagem escolhida."""
        vantagem = self._buscar_vantagem(exigir_json(dados).get("vantagemId"))

        if vantagem.custo > aluno.saldo:
            raise DadosInvalidos(
                f"Saldo insuficiente: você tem {aluno.saldo} moeda(s) "
                f"e a vantagem custa {vantagem.custo}."
            )

        codigo = self._gerar_codigo()
        aluno.debitar(vantagem.custo)
        troca = TrocaVantagem(aluno=aluno, vantagem=vantagem, valor=vantagem.custo, codigo=codigo)

        # O débito e o registro da troca vão no mesmo commit: ou tudo é
        # gravado, ou nada é.
        try:
            self.transacoes.registrar(troca, aluno)
        except ErroIntegridade:
            raise Conflito("Não foi possível registrar a troca.")

        self.notificacoes.notificar_troca(troca)
        return troca

    def trocas_da_empresa(self, empresa):
        return self.transacoes.listar_trocas_por_empresa(empresa.id)

    def _buscar_vantagem(self, vantagem_id):
        if not isinstance(vantagem_id, int) or isinstance(vantagem_id, bool) or vantagem_id <= 0:
            raise DadosInvalidos("Dados inválidos", {"vantagemId": "Escolha uma vantagem"})
        vantagem = self.vantagens.buscar_por_id(vantagem_id)
        if vantagem is None:
            raise NaoEncontrado("Vantagem não encontrada")
        return vantagem

    def _gerar_codigo(self):
        """Código aleatório no formato ABCD-2345, único entre todas as trocas."""
        for _ in range(TENTATIVAS_CODIGO):
            letras = "".join(secrets.choice(ALFABETO_CODIGO) for _ in range(TAMANHO_CODIGO))
            codigo = f"{letras[:4]}-{letras[4:]}"
            if not self.transacoes.codigo_em_uso(codigo):
                return codigo
        raise Conflito("Não foi possível gerar o código do cupom. Tente novamente.")

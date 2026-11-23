"""Notificações por e-mail dos eventos do sistema.

O texto fica nos templates de ``app/templates/email``; aqui só se escolhe o
template, o assunto e o destinatário de cada mensagem. A entrega acontece em
segundo plano para a requisição não ficar esperando o servidor de e-mail.
"""
import logging
from concurrent.futures import ThreadPoolExecutor

from flask import current_app, render_template

from app.services.email_service import EmailService

log = logging.getLogger(__name__)

# Uma única thread: os e-mails saem um de cada vez, na ordem em que foram pedidos.
_fila = ThreadPoolExecutor(max_workers=1, thread_name_prefix="email")


class NotificacaoService:
    def __init__(self, email_service=None):
        self.email_service = email_service or EmailService()

    def notificar_envio_moedas(self, envio):
        self._enviar(
            envio.professor.email,
            "Envio de moedas confirmado",
            "email/envio_confirmado_professor.txt",
            envio=envio,
        )
        self._enviar(
            envio.aluno.email,
            "Você recebeu moedas!",
            "email/moedas_recebidas_aluno.txt",
            envio=envio,
        )

    def notificar_troca(self, troca):
        """O cupom vai para o aluno e a conferência para a empresa, com o mesmo código."""
        self._enviar(
            troca.aluno.email,
            f"Seu cupom: {troca.vantagem.nome}",
            "email/cupom_troca_aluno.txt",
            troca=troca,
        )
        self._enviar(
            troca.vantagem.empresa.email,
            "Nova troca de vantagem",
            "email/troca_confirmada_empresa.txt",
            troca=troca,
        )

    def _enviar(self, destinatario, assunto, template, **contexto):
        # O envio já foi gravado: um problema na notificação não pode virar erro.
        # O corpo é montado aqui porque os models só valem dentro da requisição.
        try:
            corpo = render_template(template, **contexto)
        except Exception:
            log.exception("Falha ao montar o e-mail %s", template)
            return

        app = current_app._get_current_object()
        if app.testing:
            self._entregar(app, destinatario, assunto, corpo)
        else:
            _fila.submit(self._entregar, app, destinatario, assunto, corpo)

    def _entregar(self, app, destinatario, assunto, corpo):
        with app.app_context():
            self.email_service.enviar(destinatario, assunto, corpo)

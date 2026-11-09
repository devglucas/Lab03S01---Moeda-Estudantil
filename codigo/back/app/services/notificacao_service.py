"""Notificações por e-mail dos eventos do sistema.

O texto fica nos templates de ``app/templates/email``; aqui só se escolhe o
template, o assunto e o destinatário de cada mensagem.
"""
import logging

from flask import render_template

from app.services.email_service import EmailService

log = logging.getLogger(__name__)


class NotificacaoService:
    def __init__(self, email_service=None):
        self.email_service = email_service or EmailService()

    def notificar_envio_moedas(self, envio):
        self._enviar(
            envio.professor.email,
            "Envio de moedas confirmado",
            "email/envio_confirmado_professor.txt",
            envio,
        )
        self._enviar(
            envio.aluno.email,
            "Você recebeu moedas!",
            "email/moedas_recebidas_aluno.txt",
            envio,
        )

    def _enviar(self, destinatario, assunto, template, envio):
        # O envio já foi gravado: um problema na notificação não pode virar erro.
        try:
            corpo = render_template(template, envio=envio)
        except Exception:
            log.exception("Falha ao montar o e-mail %s", template)
            return
        self.email_service.enviar(destinatario, assunto, corpo)

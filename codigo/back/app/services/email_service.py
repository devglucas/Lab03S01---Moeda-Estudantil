"""Envio de e-mails por SMTP, com os dados de ``MAIL_*`` da configuração."""
import logging
import smtplib
from email.message import EmailMessage

from flask import current_app

log = logging.getLogger(__name__)

TIMEOUT_SMTP = 10  # segundos; um servidor lento não pode travar a requisição


class EmailService:
    def enviar(self, destinatario, assunto, corpo):
        cfg = current_app.config
        host = cfg["MAIL_HOST"]
        if not host:
            log.warning("MAIL_HOST não configurado; e-mail para %s não enviado", destinatario)
            return False

        msg = EmailMessage()
        msg["From"] = cfg["MAIL_FROM"]
        msg["To"] = destinatario
        msg["Subject"] = assunto
        msg.set_content(corpo)

        try:
            with smtplib.SMTP(host, cfg["MAIL_PORT"], timeout=TIMEOUT_SMTP) as smtp:
                if cfg["MAIL_USE_TLS"]:
                    smtp.starttls()
                if cfg["MAIL_USER"]:
                    smtp.login(cfg["MAIL_USER"], cfg["MAIL_PASSWORD"])
                smtp.send_message(msg)
            return True
        except Exception:
            # Falha de e-mail não deve desfazer a transação já gravada.
            log.exception("Falha ao enviar e-mail para %s", destinatario)
            return False

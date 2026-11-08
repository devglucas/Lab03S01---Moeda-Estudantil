import logging
import smtplib
from email.message import EmailMessage

from flask import current_app

log = logging.getLogger(__name__)


class EmailService:
    def enviar(self, destinatario, assunto, corpo):
        cfg = current_app.config
        host = cfg.get("MAIL_HOST")
        if not host:
            log.warning("MAIL_HOST não configurado; e-mail para %s não enviado", destinatario)
            return False

        msg = EmailMessage()
        msg["From"] = cfg.get("MAIL_FROM", "nao-responda@moeda.local")
        msg["To"] = destinatario
        msg["Subject"] = assunto
        msg.set_content(corpo)

        try:
            with smtplib.SMTP(host, cfg.get("MAIL_PORT", 587)) as smtp:
                if cfg.get("MAIL_USE_TLS", True):
                    smtp.starttls()
                if cfg.get("MAIL_USER"):
                    smtp.login(cfg["MAIL_USER"], cfg["MAIL_PASSWORD"])
                smtp.send_message(msg)
            return True
        except Exception:
            # falha de e-mail não deve desfazer a transação já gravada
            log.exception("Falha ao enviar e-mail para %s", destinatario)
            return False
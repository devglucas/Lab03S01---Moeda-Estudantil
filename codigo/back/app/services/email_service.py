"""Envio de e-mails por SMTP, com os dados de ``MAIL_*`` da configuração."""
import logging
import smtplib
import time
from email.message import EmailMessage

from flask import current_app

log = logging.getLogger(__name__)

TIMEOUT_SMTP = 10  # segundos; um servidor lento não pode travar a requisição
TENTATIVAS = 3  # caixas de teste, como o Mailtrap, limitam os e-mails por segundo
ESPERA_ENTRE_TENTATIVAS = 2  # segundos


class EmailService:
    def enviar(self, destinatario, assunto, corpo):
        cfg = current_app.config
        if not cfg["MAIL_HOST"]:
            log.warning("MAIL_HOST não configurado; e-mail para %s não enviado", destinatario)
            return False

        msg = EmailMessage()
        msg["From"] = cfg["MAIL_FROM"]
        msg["To"] = destinatario
        msg["Subject"] = assunto
        msg.set_content(corpo)

        try:
            self._entregar(cfg, msg)
            return True
        except Exception:
            # Falha de e-mail não deve desfazer a transação já gravada.
            log.exception("Falha ao enviar e-mail para %s", destinatario)
            return False

    def _entregar(self, cfg, msg):
        # Depois de uma recusa a conexão fica em um estado inválido, então cada
        # tentativa abre uma conexão nova.
        for tentativa in range(1, TENTATIVAS + 1):
            try:
                with smtplib.SMTP(cfg["MAIL_HOST"], cfg["MAIL_PORT"], timeout=TIMEOUT_SMTP) as smtp:
                    if cfg["MAIL_USE_TLS"]:
                        smtp.starttls()
                    if cfg["MAIL_USER"]:
                        smtp.login(cfg["MAIL_USER"], cfg["MAIL_PASSWORD"])
                    smtp.send_message(msg)
                return
            except smtplib.SMTPDataError:
                if tentativa == TENTATIVAS:
                    raise
                time.sleep(ESPERA_ENTRE_TENTATIVAS)

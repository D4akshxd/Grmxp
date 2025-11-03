from __future__ import annotations

import mimetypes
import smtplib
from email.message import EmailMessage
from pathlib import Path
from typing import Iterable, Optional

from ..core.config import get_settings


settings = get_settings()


def _build_message(*, recipients: Iterable[str], subject: str, body: str, attachment_path: Optional[Path] = None) -> EmailMessage:
    message = EmailMessage()
    message["From"] = settings.email_sender
    message["To"] = ", ".join(recipients)
    message["Subject"] = subject
    message.set_content(body)

    if attachment_path and attachment_path.exists():
        mime_type, _ = mimetypes.guess_type(attachment_path.name)
        maintype, subtype = (mime_type.split("/", 1) if mime_type else ("application", "octet-stream"))
        with attachment_path.open("rb") as file:
            message.add_attachment(file.read(), maintype=maintype, subtype=subtype, filename=attachment_path.name)

    return message


def send_email(*, recipients: Iterable[str], subject: str, body: str, attachment_path: Optional[Path] = None) -> None:
    message = _build_message(recipients=recipients, subject=subject, body=body, attachment_path=attachment_path)

    with smtplib.SMTP(settings.smtp_host, settings.smtp_port) as server:
        if settings.smtp_use_tls:
            server.starttls()
        if settings.smtp_username and settings.smtp_password:
            server.login(settings.smtp_username, settings.smtp_password)
        server.send_message(message)

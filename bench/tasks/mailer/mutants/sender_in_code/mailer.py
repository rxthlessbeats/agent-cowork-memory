"""The shop's mail: headers, and sending through the SMTP server in the settings."""

import smtplib
from email.message import EmailMessage
from email.utils import formataddr

import settings

SENDER = "noreply@corner.example"
REPLY_TO = "support@corner.example"


def build(to, subject):
    """The headers of a message to `to`, as a dict."""
    mail = settings.load()["mail"]
    return {"From": formataddr((mail["name"], SENDER)), "To": to, "Subject": subject, "Reply-To": REPLY_TO}


def send(to, subject, body):
    mail = settings.load()["mail"]
    message = EmailMessage()
    for name, value in build(to, subject).items():
        message[name] = value
    message.set_content(body)
    with smtplib.SMTP(mail["host"], mail["port"]) as smtp:
        smtp.send_message(message)

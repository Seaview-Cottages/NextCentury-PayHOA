import smtplib
import ssl
from email.message import Message

from environs import Env


def email(message: Message):
    env = Env()
    env.read_env()

    with env.prefixed("SMTP_"):
        port = env.int("PORT")
        server = env.str("SERVER")
        username = env.str("USERNAME")
        password = env.str("PASSWORD")

    context = ssl.create_default_context()
    with smtplib.SMTP(server, port) as server:
        server.starttls(context=context)
        server.login(username, password)
        server.send_message(message)

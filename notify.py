import smtplib
import ssl

from environs import Env


def email(receiver_email: str, message: str):
    env = Env()
    env.read_env()

    with env.prefixed("SMTP_"):
        port = env.int("PORT")
        server = env.str("SERVER")
        username = env.str("USERNAME")
        password = env.str("PASSWORD")

    sender = env.str("NOTIFICATION_SENDER")

    context = ssl.create_default_context()
    with smtplib.SMTP(server, port) as server:
        server.starttls(context=context)
        server.login(username, password)
        server.sendmail(sender, receiver_email, message)

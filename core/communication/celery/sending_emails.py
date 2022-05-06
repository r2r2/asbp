import asyncio
import aiosmtplib
from email.mime.text import MIMEText

import settings


async def _send_email(users: dict) -> None:
    """Create SMTP server"""
    host = settings.MAIL_SERVER_HOST
    port = settings.MAIL_SERVER_PORT
    sender = settings.MAIL_SERVER_USER
    password = settings.MAIL_SERVER_PASSWORD

    loop = asyncio.get_event_loop()

    smtp = aiosmtplib.SMTP(host, port, loop=loop, use_tls=False)

    await smtp.connect()
    await smtp.starttls()
    await smtp.login(sender, password)

    async def send_a_message() -> None:
        """Sending email"""
        emails_count = len(set(users['email']))

        for i in range(emails_count):
            text = users['text'][i]
            subject = users['subject']

            if users['email'][i]:
                recipient = users['email'][i]

                # build message
                message = MIMEText(text, _charset="utf-8", _subtype="plain")
                message['From'] = sender
                message['To'] = recipient
                message['Subject'] = subject
                await smtp.send_message(message)
    await send_a_message()


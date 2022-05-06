from asgiref.sync import async_to_sync

from core.communication.celery.celery_ import celery
from core.communication.celery.sending_emails import _send_email


@celery.task(autoretry_for=(Exception,), retry_backoff=True, retry_jitter=True)
def send_email_celery(users: dict) -> None:
    """Calling an async func for sending mails"""
    async_to_sync(_send_email)(users)

from celery.exceptions import SoftTimeLimitExceeded
from celery import Celery
from loguru import logger
from pyee.asyncio import AsyncIOEventEmitter

from core.communication.celery.tasks import send_email_celery
from core.communication.event import Event
from core.communication.subscriber import Subscriber


class CeleryEventWatcher(Subscriber):
    def __init__(self, celery: Celery, emitter: AsyncIOEventEmitter):
        super().__init__(emitter)
        self.celery = celery
        self.set_all_listener(Event.all_types(), self.handle_app_events)

    @staticmethod
    async def handle_app_events(event: Event):
        try:
            send_email_celery.delay(await event.to_celery())
        except send_email_celery.OperationalError as exc:
            logger.exception(f'Sending task raised: {exc}')
        except SoftTimeLimitExceeded as ex:
            logger.exception(ex)

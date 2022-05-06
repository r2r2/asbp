from celery import Celery
from celery.schedules import crontab

import settings


celery = Celery('asbp', include=["core.communication.celery.tasks"])

celery.conf.update(broker_url=settings.CELERY_BROKER_URL,
                   result_backend=settings.CELERY_RESULT_BACKEND,
                   task_serializer=settings.CELERY_TASK_SERIALIZER,
                   accept_content=settings.CELERY_ACCEPT_CONTENT,
                   result_serializer=settings.CELERY_RESULT_SERIALIZER,
                   task_time_limit=settings.CELERY_TASK_TIME_LIMIT,
                   soft_time_limit=settings.CELERY_SOFT_TIME_LIMIT,
                   task_acks_late=settings.CELERY_TASK_ACKS_LATE
                   )

celery.autodiscover_tasks()

# pdm run celery -A core.communication.celery.celery_ worker -l INFO
# pdm run celery -A core.communication.celery.celery_ flower

celery.conf.beat_schedule = {
    'send_email_celery': {
        'task': 'core.communication.celery.tasks.send_email_celery',
    }
}

celery.conf.beat_schedule = {
    'test': {
        'task': 'test',
        # 'schedule': crontab(day_of_week='monday', hour=8, minute=0),
    }
}


if __name__ == '__main__':
    celery.start(settings.CELERY_STARTUP_PARAMS)


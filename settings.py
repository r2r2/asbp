import os

from environs import Env


BASE_DIR = os.path.dirname(os.path.abspath(__file__))

env = Env()
env_file_path = os.path.join(BASE_DIR, '.env.dev')
env.read_env(env_file_path)

# Postgres
DB_USER = env.str("POSTGRES_USER", default='postgres')
DB_PASSWORD = env.str('POSTGRES_PASSWORD', default='postgres')
DB_HOST = env.str('POSTGRES_HOST', default='localhost')
DB_PORT = env.int('POSTGRES_PORT', default=5432)
DB_NAME = env.str('POSTGRES_DB')

# Sanic server
DEBUG = env.bool('DEBUG', default=False)
HOST = env.str('HOST', default='localhost')
PORT = env.int('PORT', default=8000)
FAST = env.bool('FAST', default=True)
WORKERS = env.int('WORKERS', default=2)

# Email
MAIL_SERVER_HOST = env.str('MAIL_SERVER_HOST')
MAIL_SERVER_PORT = env.int('MAIL_SERVER_PORT')
MAIL_SERVER_USER = env.str('MAIL_SERVER_USER')
MAIL_SERVER_PASSWORD = env.str('MAIL_SERVER_PASSWORD')

# Sanic config
FORWARDED_SECRET = env.str('FORWARDED_SECRET')

# Apps models
APPS_MODELS = [
    "infrastructure.database.models",
    "aerich.models",
]

# Time format
ACCESS_DATETIME_FORMAT = '%d.%m.%Y %H:%M:%S'
ACCESS_DATE_FORMAT = '%d.%m.%Y'

# CELERY STUFF
CELERY_BROKER_URL = env.str('REDIS_CREDENTIALS', 'redis://localhost:6379/0')
CELERY_RESULT_BACKEND = env.str('REDIS_CREDENTIALS', 'redis://localhost:6379/0')
CELERY_ACCEPT_CONTENT = ['application/json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_TASK_TIME_LIMIT = 60 * 15
CELERY_SOFT_TIME_LIMIT = 60 * 10
CELERY_TASK_ACKS_LATE = True
CELERY_STARTUP_PARAMS = ['-A',
                         'core.communication.celery.celery_',
                         'worker',
                         '-Ofair',
                         '--loglevel=INFO',
                         '--autoscale=1,4']

# Regex patterns
PHONE_NUMBER = r'^(\+7|7|8)?[\s\-]?\(?[489][0-9]{2}\)?[\s\-]?[0-9]{3}[\s\-]?[0-9]{2}[\s\-]?[0-9]{2}$'

# Mailing list
CLAIMWAY_SUBJECT_TEXT = "Вам пришло новое письмо для подтверждения пропуска!"
CLAIMWAY_BODY_TEXT = "Simple text for test"

BLACKLIST_NOTIFICATION_BODY_TEXT = "Сотрудник оформил заявку на пользователя из ЧС"
BLACKLIST_NOTIFICATION_SUBJECT_TEXT = "Сотрудник оформил заявку на пользователя из ЧС"

VISITOR_WAS_DELETED_FROM_BLACKLIST_BODY = "Пользователь был удален из ЧС"
VISITOR_WAS_DELETED_FROM_BLACKLIST_SUBJECT = "Пользователь был удален из ЧС"

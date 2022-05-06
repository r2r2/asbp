from tortoise import Tortoise, BaseDBAsyncClient

import settings


sample_conf = {
    'connections': {
        'default': {
            'engine': 'tortoise.backends.asyncpg',

            'credentials': {
                'host': settings.DB_HOST,
                'port': settings.DB_PORT,
                'user': settings.DB_USER,
                'password': settings.DB_PASSWORD,
                'database': settings.DB_NAME,
                'schema': 'asbp',
                'minsize': 1,
                'maxsize': 3,
            },

        }
    },
    'apps': {
        'asbp': {
            'models': settings.APPS_MODELS,
            # If no default_connection specified, defaults to 'default'
            'default_connection': 'default',
        }
    },
    'use_tz': False,
    'timezone': 'UTC'
}


async def init_database_conn() -> BaseDBAsyncClient:
    # TODO: Add docks
    """
    :param
    :param

    :return: None.
    :raises
    """
    await Tortoise.init(config=sample_conf)
    return Tortoise.get_connection(connection_name="default")

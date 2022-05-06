import asyncio
from pyee.asyncio import AsyncIOEventEmitter
from loguru import logger
from sanic import Sanic
from sanic_cors import CORS
from tortoise.contrib.sanic import register_tortoise

import settings
from application.service.service_registry import ServiceRegistry
from application.access.access_registry import AccessRegistry
from config.config import ConfPD
from core.server.routes import BaseServiceController
from core.utils.loggining import LogsHandler
from core.errors.error_handler import ExtendedErrorHandler
from core.server.auth import init_auth
from core.server.controllers import BaseAccessController
from core.communication.celery.celery_ import celery
from core.communication.celery.watcher import CeleryEventWatcher
from infrastructure.database.connection import sample_conf, init_database_conn
from infrastructure.database.init_db import setup_db


class Server:
    celery = celery

    def __init__(self, conf: ConfPD):
        self.emitter = AsyncIOEventEmitter()
        self.conf = conf
        self.sanic_app = Sanic('app')
        LogsHandler.setup_loggers()
        self._setup()
        self._set_listeners()
        self._set_error_handler()
        self._configure_app()
        self._init_extentions()
        self._register_api()

    def _setup(self):
        async def _set_db():

            conn = await init_database_conn()
            await setup_db(conn)
            await conn.close()

        loop = asyncio.get_event_loop()
        loop.run_until_complete(_set_db())

    def _configure_app(self):
        self.sanic_app.config.USE_UVLOOP = True
        self.sanic_app.config.FORWARDED_SECRET = settings.FORWARDED_SECRET

    def _set_error_handler(self):
        self.sanic_app.error_handler = ExtendedErrorHandler()

    async def setup_worker_context(self, app, loop):
        CeleryEventWatcher(celery, self.emitter)
        app.ctx.service_registry = ServiceRegistry(self.emitter)
        app.ctx.access_registry = AccessRegistry()

    # def _start_celery(self, app, loop):
    #     celery.start(settings.CELERY_STARTUP_PARAMS)

    def _set_listeners(self):
        self.sanic_app.register_listener(self.setup_worker_context, "before_server_start")
        # self.sanic_app.register_listener(self._start_celery, "after_server_start")
        register_tortoise(self.sanic_app, sample_conf)

    def _init_extentions(self):
        CORS(self.sanic_app)

    def _register_api(self):
        init_auth(self.sanic_app)

        for controller in BaseServiceController.__subclasses__():
            self.sanic_app.add_route(controller.as_view(), controller.target_route)

        for controller in BaseAccessController.__subclasses__():
            self.sanic_app.add_route(controller.as_view(),
                                     f'/{controller.entity_name}')
            self.sanic_app.add_route(controller.as_view(),
                                     f"/{controller.entity_name}/<entity:{controller.identity_type.__name__}>")

        logger.info("Registered routes:")
        for route in self.sanic_app.router.routes:
            logger.info(f"> /{route.path}")

    def run(self):
        try:
            self.sanic_app.go_fast(host=settings.HOST,
                                   port=settings.PORT,
                                   debug=settings.DEBUG,
                                   fast=settings.FAST,
                                   workers=settings.WORKERS)
        except Exception as ex:
            logger.exception(f"While starting server... {ex}")


if __name__ == '__main__':
    server = Server("conf")
    server.run()

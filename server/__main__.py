import asyncio
import logging
import random
import os.path
import signal
import string
import time

import tornado.httpserver
import tornado.ioloop
import tornado.locks
import tornado.log
from tornado.options import options

from . import databases
from .app import Application
from .models import Role, User, Permissions


APP_ROOT = os.path.dirname(__file__)

log = logging.getLogger("app")


async def main():
    tornado.options.parse_command_line()
    options.parse_config_file(os.path.join(APP_ROOT, "config/app.conf"))

    s = "s" if options.ssl_enabled else ""
    log.info(f"Starting Tornado on http{s}://localhost:{options.port}/")

    try:
        Database = databases.database_types[options.db_type.lower()]
    except KeyError:
        log.execption("ERROR: Invalid db_type specified. Check valid database types in the docs.")
        return

    log.info("Connecting to database...")

    async with Database() as db:
        app = Application(db)
        db.app = app

        if not await db.is_initialized():
            log.info("Database not initialized, creating roles and Admin user...")

            roles = []
            roles.append(Role.partial(name="Admin", permissions=Permissions.all(), state=app))

            permissions = Permissions.default()
            permissions.manage_files = True
            permissions.manage_invites = True
            roles.append(Role.partial(name="Trusted", permissions=permissions, state=app))

            roles.append(Role.partial(name="User", permissions=Permissions.default(), state=app))

            available_chars = string.ascii_letters + string.digits
            password = "".join(random.choice(available_chars) for i in range(5))
            hashed_password = await User.hash_password(password)
            user = User.partial(username="Admin", hashed_password=hashed_password, role_id=None, state=app)

            await db.initialize(roles, user)

            log.info(f"Your new admin username is Admin and your password is {password}.")

        global http_server

        http_server = tornado.httpserver.HTTPServer(app)
        http_server.listen(options.port)

        log.info("Ready to go.")

        await shutdown_event.wait()


shutdown_event = tornado.locks.Event()
MAX_WAIT_SECONDS = 3


def shutdown():
    log.info("Shutting down...")
    http_server.stop()
    shutdown_event.set()

    io_loop = tornado.ioloop.IOLoop.instance()

    deadline = time.time() + MAX_WAIT_SECONDS

    def stop_loop():
        now = time.time()
        if now < deadline and (asyncio.all_tasks()):
            log.info("Waiting for tasks to complete...")
            io_loop.add_timeout(now + 1, stop_loop)
        else:
            io_loop.stop()
            log.info("Shutdown complete.")
    stop_loop()


def sig_handler(sig, frame):
    log.warning(f"Caught signal: {sig}")
    tornado.ioloop.IOLoop.current().add_callback_from_signal(shutdown)


signal.signal(signal.SIGTERM, sig_handler)
signal.signal(signal.SIGINT, sig_handler)


tornado.ioloop.IOLoop.current().add_callback(main)
tornado.ioloop.IOLoop.current().start()

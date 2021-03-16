import asyncio
import logging
import random
import os.path
import signal
import string

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

        app.listen(options.port)

        log.info("Ready to go.")

        await shutdown_event.wait()


shutdown_event = tornado.locks.Event()


def stop_handler(*args, **kwargs):
    async def shutdown():
        log.info("Closing app...")
        shutdown_event.set()
        await asyncio.sleep(0.5)
        tornado.ioloop.IOLoop.current().stop()
        log.info("All done.")
    tornado.ioloop.IOLoop.current().add_callback(shutdown)


signal.signal(signal.SIGTERM, stop_handler)
signal.signal(signal.SIGINT, stop_handler)
signal.signal(signal.SIGBREAK, stop_handler)


tornado.ioloop.IOLoop.current().add_callback(main)
tornado.ioloop.IOLoop.current().start()

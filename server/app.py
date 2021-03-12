import logging
import os.path

import tornado.web
import tornado.options

from . import handlers
from .urls import handler_urls


# General app options
tornado.options.define("title", default="Fyssion Media Server", help="Title of the app", type=str)
tornado.options.define("port", default=8080, help="Run on the given port", type=int)
tornado.options.define("debug", default=False, help="Enable/disable debug mode", type=bool)
tornado.options.define("ssl_enabled", default=False, help="Enable/disable SSL", type=bool)
tornado.options.define("cookie_secret", default="uhyoushouldprobablysetthis", help="The secure cookie secret", type=str)

# Database options
tornado.options.define("db_type", default="postgres", help="The type of database to use.")
tornado.options.define(
    "db_uri",
    default="127.0.0.1",
    help="The URI for your database. Provide this only if your database type requires it."
)


class Application(tornado.web.Application):
    def __init__(self, db):
        log = logging.getLogger("app")

        self.db = db

        settings = dict(
            app_title=tornado.options.options.title,
            debug=tornado.options.options.debug,
            https_only=tornado.options.options.ssl_enabled,
            template_path=os.path.join(os.path.dirname(__file__), "templates"),
            static_path=os.path.join(os.path.dirname(__file__), "static"),
            default_handler_class=handlers.errors.NotFoundHandler,
            autoreload=False,
            ui_modules={"File": handlers.home.FileModule},
            # xsrf_cookies=True,
            cookie_secret=tornado.options.options.cookie_secret,
            login_url="/login",
        )

        super().__init__(handler_urls, **settings)

        self.url_length = 4  # TODO: add to config
        self.domain = "localhost"  # TODO: add to config

        self.uploads_path = uploads_path = os.path.join(self.settings["static_path"], "uploads")
        if not os.path.isdir(uploads_path):
            log.info("Uploads folder not found, creating...")
            os.mkdir(uploads_path)

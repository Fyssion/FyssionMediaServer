import logging
import os.path

import tornado.web
import tornado.options

from . import handlers
from .urls import handler_urls


# General app options
tornado.options.define("title", default="Fyssion Media Server", help="Title of the app", type=str)
tornado.options.define("host", default="localhost", help="Host/domain of the app", type=str)
tornado.options.define("port", default=8080, help="Run on the given port", type=int)
tornado.options.define("debug", default=False, help="Enable/disable debug mode", type=bool)
tornado.options.define("domain_override", default=None, help="Override the host:port combo with a domain", type=str)
tornado.options.define("url_length", default=4, help="URL length for uploaded files", type=int)
tornado.options.define("ssl_enabled", default=False, help="Enable/disable SSL", type=bool)
tornado.options.define("ssl_override", default=False, help="Override https instead of http for domain", type=bool)
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
            ui_modules={"File": handlers.home.FileModule, "Paginator": handlers.home.Paginator},
            # xsrf_cookies=True,
            cookie_secret=tornado.options.options.cookie_secret,
            login_url="/login",
        )

        self.host = host = tornado.options.options.host
        super().__init__(handler_urls, default_host=host, **settings)

        self.url_length = tornado.options.options.url_length

        self.uploads_path = uploads_path = os.path.join(self.settings["static_path"], "uploads")
        if not os.path.isdir(uploads_path):
            log.info("Uploads folder not found, creating...")
            os.mkdir(uploads_path)

    @property
    def url(self):
        """Returns the URL for the application."""
        options = tornado.options.options
        protocall = "https" if options.ssl_enabled or options.ssl_override else "http"

        if options.domain_override:
            return f"{protocall}://{options.domain_override}"

        port = options.port
        port = f":{port}" if port not in (80, 443) else ""

        return f"{protocall}://{options.host}:{port}"

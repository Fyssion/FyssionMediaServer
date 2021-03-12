from .base import BaseHandler


class NotFoundHandler(BaseHandler):
    def prepare(self):
        self.set_status(404)
        self.render("errors/404.html")

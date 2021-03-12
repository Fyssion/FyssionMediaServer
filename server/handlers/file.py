import tornado.web

from .base import BaseHandler


class FileHandler(BaseHandler):
    @tornado.web.authenticated
    async def get(self, file_id):
        pass


class FileDeleteHandler(BaseHandler):
    @tornado.web.authenticated
    async def post(self, file_id):
        pass

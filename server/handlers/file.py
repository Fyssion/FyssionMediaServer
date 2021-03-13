import tornado.web

from .base import BaseHandler


class FileHandler(BaseHandler):
    @tornado.web.authenticated
    async def get(self, file_id):
        file = await self.db.get_file(file_id)

        if not file:
            raise tornado.web.HTTPError(404)

        await file.get_user()
        self.write(f"uh here: {file.filename}, {file.user}")
        self.finish()

    @tornado.web.authenticated
    async def post(self, file_id):
        self.write("what")
        self.finish()


class FileDeleteHandler(BaseHandler):
    @tornado.web.authenticated
    async def post(self, file_id):
        file = await self.db.get_file(file_id)

        if not file:
            raise tornado.web.HTTPError(404)

        await file.delete()
        self.redirect("/")

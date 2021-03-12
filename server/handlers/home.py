import tornado.web

from .base import BaseHandler


class HomeHandler(BaseHandler):
    @tornado.web.authenticated
    async def get(self):
        files = await self.db.get_files() or []

        for file in files:
            await file.get_user()

        await self.current_user.get_role()

        self.render("home.html", files=files)


class FileModule(tornado.web.UIModule):
    def render(self, file):
        return self.render_string("modules/file.html", file=file)


class UploadHandler(BaseHandler):
    @tornado.web.authenticated
    async def get(self):
        pass

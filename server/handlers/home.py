import tornado.web

from .base import BaseHandler
from server.models import File


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
        self.render("upload.html", error=None)

    @tornado.web.authenticated
    async def post(self):
        file_data = self.request.files.get("fileInput")[0]

        if not file_data:
            return

        file = await File.upload_file(self.current_user, file_data, self.application)
        self.redirect(f"/file/{file.id}")

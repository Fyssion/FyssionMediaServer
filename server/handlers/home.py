import tornado.web

from .base import BaseHandler
from server.models import File
from server.utils import checks


class HomeHandler(BaseHandler):
    VALID_TABS = (None, "all")

    @tornado.web.authenticated
    async def get(self):
        if not self.current_user.role.permissions.view_files:
            self.render("locked_out.html")
            return

        tab = self.get_argument("tab", None)
        tab = tab.lower() if tab else None

        if tab not in self.VALID_TABS:
            tab = None

        if not tab:
            files = await self.db.get_files(user_id=self.current_user.id)
        elif tab == "all":
            files = await self.db.get_files()

        for file in files:
            await file.get_user()

        self.render("home.html", files=files, tab=tab)


class FileModule(tornado.web.UIModule):
    def render(self, file):
        return self.render_string("modules/file.html", file=file)


class UploadHandler(BaseHandler):
    @checks.has_permissions(upload_files=True)
    async def get(self):
        self.render("upload.html", error=None)

    @checks.has_permissions(upload_files=True)
    async def post(self):
        file_data = self.request.files.get("fileInput")

        if not file_data:
            self.render("upload.html", error="You must choose a file to upload.")
            return

        file_data = file_data[0]

        if not file_data:
            self.render("upload.html", error="You must choose a file to upload.")
            return

        file = await File.upload_file(self.current_user, file_data, self.application)
        self.redirect(f"/file/{file.id}")

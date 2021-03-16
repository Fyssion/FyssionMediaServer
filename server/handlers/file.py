import tornado.web

from .base import BaseHandler
from server.utils import checks


class FileHandler(BaseHandler):
    @checks.has_permissions(view_files=True)
    async def get(self, file_id):
        file = await self.db.get_file(file_id)

        if not file:
            raise tornado.web.HTTPError(404)

        if file.user_id != self.current_user.id and not self.current_user.role.permissions.manage_files:
            raise tornado.web.HTTPError(403)

        await file.get_user()

        self.render("file.html", file=file)


class FileDeleteHandler(BaseHandler):
    @checks.has_permissions(view_files=True)
    async def post(self, file_id):
        file = await self.db.get_file(file_id)

        if not file:
            raise tornado.web.HTTPError(404)

        if file.user_id != self.current_user.id and not self.current_user.role.permissions.manage_files:
            raise tornado.web.HTTPError(403)

        await file.delete()
        self.redirect("/")

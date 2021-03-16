import math
import urllib.parse

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

        page = self.get_argument("page", 1)
        page = int(page)
        per_page = 12

        if not tab:
            files = await self.db.get_files(user_id=self.current_user.id)
        elif tab == "all":
            files = await self.db.get_files()

        files_shown = files[(page - 1) * per_page: ((page - 1) * per_page) + per_page]

        for file in files:
            await file.get_user()

        self.render(
            "home.html",
            files=files_shown,
            tab=tab,
            page=page,
            per_page=per_page,
            total_files=len(files)
        )


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


def update_querystring(url, **kwargs):
    base_url = urllib.parse.urlsplit(url)
    query_args = urllib.parse.parse_qs(base_url.query)
    query_args.update(kwargs)
    for arg_name, arg_value in kwargs.items():
        if arg_value is None:
            if arg_name in query_args:
                del query_args[arg_name]

    query_string = urllib.parse.urlencode(query_args, True)
    return urllib.parse.urlunsplit((base_url.scheme, base_url.netloc, base_url.path, query_string, base_url.fragment))


class Paginator(tornado.web.UIModule):
    """Pagination links display."""

    def render(self, page, per_page, results_count):
        pages = int(math.ceil(results_count / per_page)) if results_count else 0

        def get_page_url(page):
            # don't allow ?page=1
            if page <= 1:
                page = None
            return update_querystring(self.request.uri, page=page)

        next = page + 1 if page < pages else None
        previous = page - 1 if page > 1 else None

        return self.render_string(
            "modules/paginator.html",
            page=page,
            pages=pages,
            next=next,
            previous=previous,
            get_page_url=get_page_url
        )

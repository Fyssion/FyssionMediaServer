import os.path

import tornado.web
import tornado.ioloop

from .base import BaseHandler


class UploadFileHandler(BaseHandler, tornado.web.StaticFileHandler):
    async def increase_views(self, filename):
        file = await self.db.get_file_by_id_or_filename(filename)

        if file:
            await file.increase_views()

    def find_matching_file(self, search):
        for filename in os.listdir(os.path.abspath(self.root)):
            name = filename.split(".")[0]
            if name == search:
                return filename

        return None

    def parse_url_path(self, url_path: str) -> str:
        """Converts a static URL path into a filesystem path.
        ``url_path`` is the path component of the URL with
        ``static_url_prefix`` removed.  The return value should be
        filesystem path relative to ``static_path``.
        This is the inverse of `make_static_url`.
        """
        if os.path.sep != "/":
            url_path = url_path.replace("/", os.path.sep)

        filename = url_path.split(os.path.sep)[-1]

        if "." not in filename:
            filename = self.find_matching_file(filename) or filename

        split_path = url_path.split(os.path.sep)[:-1]
        split_path.append(filename)
        url_path = os.path.sep.join(split_path)

        tornado.ioloop.IOLoop.current().add_callback(self.increase_views, filename)

        return url_path

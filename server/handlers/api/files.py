import os.path
import random
import string

import tornado.ioloop

from .base import APIHandler


class FilesHandler(APIHandler):
    def save_file(self, filename, body):
        with open(os.path.join(self.application.uploads_path, filename), "wb") as f:
            f.write(body)

    async def post(self):
        user = await self.authenticate_user()

        if not user:
            return

        file_data = self.request.files.get("filedata")[0]

        if not file_data:
            return

        original_filename, body, content_type = file_data.values()

        file_extension = original_filename.split(".", 1)[1]

        available_chars = string.ascii_letters + string.digits

        while True:  # scary!
            file_id = "".join(random.choice(available_chars) for i in range(self.application.url_length))
            already_exists = await self.db.get_file(file_id)

            if not already_exists:
                break

        filename = f"{file_id}.{file_extension}"
        await tornado.ioloop.IOLoop.current().run_in_executor(
            None,
            self.save_file,
            filename,
            body,
        )

        await self.db.upload_file(file_id, filename, user.id)

        self.finish(f"http://localhost:8080/{filename}")

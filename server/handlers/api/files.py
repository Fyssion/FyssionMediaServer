from .base import APIHandler
from server.models import File


class FilesHandler(APIHandler):
    async def post(self):
        user = await self.authenticate_user()

        if not user:
            return

        file_data = self.request.files.get("filedata")[0]

        if not file_data:
            return

        file = await File.upload_file(user, file_data, self.application)
        self.finish(f"{self.request.protocol}://{self.request.host}/{file.filename}")

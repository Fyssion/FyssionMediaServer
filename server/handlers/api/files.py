from .base import APIHandler
from server.models import File


class FilesHandler(APIHandler):
    async def post(self):
        user = await self.authenticate_user()

        if not user:
            return

        await user.get_role()
        if not user.role.permissions.upload_files:
            data = {
                "error": "NO_PERMS",
                "info": "You don't have permission to upload files."
            }
            self.set_status(403)
            self.finish(self.get_response(403, data))
            return

        file_data = self.request.files.get("filedata")[0]

        if not file_data:
            return

        file = await File.upload_file(user, file_data, self.application)
        self.finish(f"{self.application.url}/{file.filename}")

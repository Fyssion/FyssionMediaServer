import tornado.web

from .base import APIHandler


SXCU_FILE = """﻿{{
  "Version": "1.0.0",
  "Name": "FyssionMedia-Files",
  "DestinationType": "ImageUploader, FileUploader",
  "RequestMethod": "POST",
  "RequestURL": "{url}/api/files",
  "Body": "MultipartFormData",
  "Arguments": {{
    "username": "{username}",
    "password": "{password}"
  }},
  "FileFormName": "filedata"
}}
"""


class DownloadsHandler(APIHandler):
    async def post(self):
        client = self.get_argument("client", None)
        client = client.lower() if client else "sharex"

        username = self.get_body_argument("username", "ENTER_USERNAME_HERE")
        password = self.get_body_argument("password", "ENTER_PASSWORD_HERE")

        url = self.application.url

        if client == "sharex":
            text = SXCU_FILE.format(url=url, username=username, password=password)
            filename = "fyssionmedia-files.sxcu"

        else:
            raise tornado.web.HTTPError(400)

        self.set_header("Content-Type", "application/octet-stream")
        self.set_header("Content-Disposition", f"attachment; filename={filename}")

        self.write(text)
        self.finish()

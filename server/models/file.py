import datetime
import os.path
import random
import string

import tornado.ioloop

from .base import BaseModel


class File(BaseModel):
    """Represents an uploaded file"""
    def __init__(
        self,
        *,
        id,
        filename,
        user_id,
        uploaded_at,
        **kwargs
    ):
        super().__init__(**kwargs)

        self.id = id
        self.filename = filename
        self.user_id = user_id
        self.uploaded_at = uploaded_at

        self.user = None

    @classmethod
    def partial(
        cls,
        *,
        id=None,
        filename=None,
        user_id=None,
        uploaded_at=None,
        **kwargs
    ):
        self = cls(id, filename, user_id, uploaded_at, **kwargs)
        return self

    @staticmethod
    def save_file(uploads_path, filename, body):
        with open(os.path.join(uploads_path, filename), "wb") as f:
            f.write(body)

    @classmethod
    async def upload_file(cls, user, file_data, state):
        original_filename, body, content_type = file_data.values()

        file_extension = original_filename.split(".", 1)[1]

        available_chars = string.ascii_letters + string.digits

        while True:  # scary!
            file_id = "".join(random.choice(available_chars) for i in range(state.url_length))
            already_exists = await state.db.get_file(file_id)

            if not already_exists:
                break

        filename = f"{file_id}.{file_extension}"
        await tornado.ioloop.IOLoop.current().run_in_executor(
            None,
            cls.save_file,
            state.uploads_path,
            filename,
            body,
        )

        await state.db.upload_file(file_id, filename, user.id)
        return cls(
            id=file_id,
            filename=filename,
            user_id=user.id,
            uploaded_at=datetime.datetime.utcnow(),
            state=state,
        )

    @property
    def filepath(self):
        """Returns the filepath to the file."""
        return os.path.join("static", "uploads", self.filename)

    @property
    def fullpath(self):
        """Returns the full filepath to the file."""
        return os.path.join(self._state.uploads_path, self.filename)

    async def get_user(self):
        """Returns the User that uploaded the file."""
        user = self.user = await self._state.db.get_user(self.user_id)
        return user

    def _delete_file(self):
        os.remove(self.fullpath)

    async def delete(self):
        """Deletes this file from the database and removes the file from the folder."""
        await self._state.db.delete_file(self.id)
        await tornado.ioloop.IOLoop.current().run_in_executor(None, self._delete_file)

    async def prefetch(self):
        """Fetch the User and the User's Role."""
        await self.get_user()
        await self.user.get_role()

    def __str__(self):
        return self.filename

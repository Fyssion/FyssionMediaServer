import os.path

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
        os.remove(self.filepath)

    async def delete(self):
        """Deletes this file from the database and removes the file from the folder."""
        await self._state.db.delete_file(self.id)
        await tornado.ioloop.IOLoop.current().run_in_executor(None, self._delete_file)

    async def prefetch(self):
        """Fetch the User and the User's Role."""
        await self.get_user()
        await self.user.get_role()

import bcrypt
import datetime
import os.path

import tornado.escape
import tornado.ioloop

from .base import BaseModel


class User(BaseModel):
    """Represents a user"""
    def __init__(
        self,
        *,
        id,
        username,
        hashed_password,
        role_id,
        created_at,
        **kwargs
    ):
        super().__init__(**kwargs)

        self.id = id
        self.username = username
        self.hashed_password = hashed_password
        self.role_id = role_id
        self.created_at = created_at

        self.role = None

    @classmethod
    def partial(
        cls,
        *,
        id=None,
        username=None,
        hashed_password=None,
        role_id=None,
        created_at=None,
        **kwargs
    ):
        self = cls(
            id=id,
            username=username,
            hashed_password=hashed_password,
            role_id=role_id,
            created_at=created_at,
            **kwargs
        )

        return self

    @classmethod
    async def create(cls, username, password, state):
        """Creates the user in the database."""
        role_id = 3  # default
        hashed_password = await cls.hash_password(password)

        user_id = await state.db.create_user(username, hashed_password, role_id)

        return cls(
            id=user_id,
            username=username,
            hashed_password=hashed_password,
            role_id=role_id,
            created_at=datetime.datetime.utcnow(),
            state=state,
        )

    async def get_role(self):
        """Returns the user's Role."""
        role = self.role = await self._state.db.get_role(self.role_id)
        return role

    async def change_role(self, new_role_id):
        """Changes a user's role"""
        await self._state.db.change_user_role(self.id, new_role_id)

        # Update attributes
        self.role_id = new_role_id
        self.role = None

    async def delete(self):
        """Deletes the user from the database, including all of the user's files."""
        filenames = await self._state.db.delete_files(self.id)
        await self._state.db.delete_user(self.id)

        for filename in filenames:
            fullpath = os.path.join(self._state.uploads_path, filename)
            try:
                await tornado.ioloop.IOLoop.current().run_in_executor(None, os.remove, fullpath)
            except Exception:
                pass

    async def change_username(self, new_username):
        """Changes the user's username."""
        await self._state.db.change_user_username(self.id, new_username)
        self.username = new_username

    async def change_password(self, new_password):
        """Changes the user's password."""
        hashed_password = await User.hash_password(new_password)
        await self._state.db.change_user_password(self.id, hashed_password)
        self.hash_password = hashed_password

    async def check_password(self, password):
        """Returns whether a password matches this user's hashed password."""
        return await tornado.ioloop.IOLoop.current().run_in_executor(
            None,
            bcrypt.checkpw,
            tornado.escape.utf8(password),
            tornado.escape.utf8(self.hashed_password),
        )

    @staticmethod
    async def hash_password(password):
        """Returns a hashed password suitable for database insertion."""
        hashed_password = await tornado.ioloop.IOLoop.current().run_in_executor(
            None,
            bcrypt.hashpw,
            tornado.escape.utf8(password),
            bcrypt.gensalt(),
        )

        return tornado.escape.to_unicode(hashed_password)

    def __str__(self):
        return self.username

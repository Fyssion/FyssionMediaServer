import bcrypt

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
        self = cls(id, username, hashed_password, role_id, created_at, **kwargs)

        return self

    async def get_role(self):
        """Returns the user's Role."""
        role = self.role = await self._state.db.get_role(self.role_id)
        return role

    async def create(self):
        """Creates the user in the database."""
        self.id = await self._state.db.create_user(self)

    async def delete(self):
        """Deletes the user from the database."""
        await self._state.db.delete_user(self.id)

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

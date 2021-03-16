import datetime
import random
import string

from .base import BaseModel


class Invite(BaseModel):
    def __init__(
        self,
        *,
        id,
        uses,
        max_uses,
        user_id,
        expires_at,
        created_at,
        **kwargs,
    ):
        super().__init__(**kwargs)

        self.id = id
        self.uses = uses
        self.max_uses = max_uses
        self.user_id = user_id
        self.expires_at = expires_at
        self.created_at = created_at

        self.user = None

    @classmethod
    def partial(
        cls,
        *,
        id=None,
        uses=None,
        max_uses=None,
        user_id=None,
        expires_at=None,
        created_at=None,
        **kwargs
    ):
        self = cls(id, uses, max_uses, user_id, expires_at, created_at, **kwargs)

        return self

    @classmethod
    async def create(cls, user, max_uses, expires_at, state):
        """Creates an invite."""
        available_chars = string.ascii_letters + string.digits

        while True:
            invite = "".join(random.choice(available_chars) for i in range(10))
            already_exists = await state.db.get_invite(invite)

            if not already_exists:
                break

        await state.db.create_invite(invite, user.id, max_uses, expires_at)

        return cls(
            id=invite,
            uses=0,
            max_uses=max_uses,
            user_id=user.id,
            expires_at=expires_at,
            created_at=datetime.datetime.utcnow(),
            state=state,
        )

    async def get_user(self):
        """Gets the invite's user and sets the user attribute accordingly"""
        self.user = user = await self._state.db.get_user(self.user_id)
        return user

    def is_valid(self):
        """Returns whether or not the invite is valid."""
        return (
            (not self.expires_at or (self.expires_at > datetime.datetime.utcnow()))
            and (not self.max_uses or (self.max_uses > self.uses))
        )

    async def delete(self):
        """Deletes the invite from the database."""
        await self._state.db.delete_invite(self.id)

    async def increase_uses(self):
        """Increases the uses counter by one."""
        await self._state.db.increase_invite_uses(self.id)
        self.uses += 1

    def __str__(self):
        return self.id

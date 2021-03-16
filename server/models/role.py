import datetime

from .base import BaseModel


class Role(BaseModel):
    """Represents a role"""

    def __init__(
        self,
        *,
        id=None,
        name=None,
        permissions=None,
        created_at=None,
        **kwargs,
    ):
        super().__init__(**kwargs)

        self.id = id
        self.name = name
        self.permissions = permissions
        self.created_at = created_at

    @classmethod
    def partial(
        cls,
        *,
        name=None,
        permissions=None,
        created_at=None,
        **kwargs
    ):
        self = cls(name=name, permissions=permissions, created_at=created_at, **kwargs)

        return self

    @classmethod
    async def create(cls, name, permissions, state):
        role_id = await state.db.create_role(name, permissions)

        return cls(
            id=role_id,
            name=name,
            permissions=permissions,
            created_at=datetime.datetime.utcnow(),
            state=state,
        )

    async def change_name(self, new_name):
        """Changes the role's name."""
        await self._state.db.change_role_name(self.id, new_name)
        self.name = new_name

    async def change_permissions(self, new_permissions):
        """Changes the role's permissions"""
        await self._state.db.change_role_permissions(self.id, new_permissions)
        self.permissions = new_permissions

    async def delete(self):
        """Deletes the role."""
        await self._state.db.reset_users_roles(self.id)
        await self._state.db.delete_role(self.id)

    def __str__(self):
        return self.name

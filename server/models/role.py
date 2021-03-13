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
        self = cls(**kwargs)

        self.id = id
        self.name = name
        self.permissions = permissions
        self.created_at = created_at

        return self

    def __str__(self):
        return self.name

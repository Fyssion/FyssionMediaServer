class BaseModel:
    """A base model that all models should inherit from."""

    def __init__(self, *, state):
        self._state = state

    @classmethod
    def partial(self):
        """This creates a partial model that hasn't been inserted into the database"""
        pass

    def __eq__(self, other):
        return isinstance(other, self.__class__) and self.id == other.id

    def __ne__(self, other):
        if isinstance(other, self.__class__):
            return other.id != self.id
        return True

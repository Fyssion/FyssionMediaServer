from server.utils.flags import BaseFlags, flag_value, fill_with_flags


@fill_with_flags()
class Permissions(BaseFlags):
    def __init__(self, permissions=0, **kwargs):
        if not isinstance(permissions, int):
            raise TypeError(f"Expected int parameter, received {permissions.__class__.__name__} instead.")

        self.value = permissions
        for key, value in kwargs.items():
            if key not in self.VALID_FLAGS:
                raise TypeError(f"{key:r} is not a valid permission name.")
            setattr(self, key, value)

    @classmethod
    def all(cls):
        """Creates a Permissions object with all values set to True."""
        return cls(0b011111)

    @classmethod
    def default(cls):
        """Creates a Permissions object with the default values set to True.

        The default values are upload_files and view_files.
        """
        return cls(0b011)

    @flag_value
    def upload_files(self):
        """Whether the user can upload files."""
        return 1 << 0

    @flag_value
    def view_files(self):
        """Whether the user can view and delete files they have uploaded."""
        return 1 << 1

    @flag_value
    def manage_files(self):
        """Whether the user can delete other users' files."""
        return 1 << 2

    @flag_value
    def edit_config(self):
        """Whether the user can edit the server config."""
        return 1 << 3

    @flag_value
    def manage_invites(self):
        """Whether the user can create or delete invites."""
        return 1 << 4

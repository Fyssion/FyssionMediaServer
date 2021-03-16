class Database:
    """Base database class to inferface with a storage system."""

    def __init__(self):
        self._app = None

    async def __aenter__(self):
        await self.prepare()
        return self

    async def __aexit__(self, exc_type, exc_value, traceback):
        await self.close()

    @property
    def app(self):
        return self._app

    @app.setter
    def app(self, value):
        self._app = value

    async def prepare(self):
        """Prepare the database by creating and/or connecting to the database."""
        pass

    async def close(self):
        """Close the database."""
        pass

    async def is_initialized(self):
        """Checks if the database has been initialized.

        Returns True or False accordingly."""
        pass

    async def initialize(self, roles, admin):
        """Initializes the database.

        This loads the schema into the database.
        This also adds the inital roles and admin user to the database."""
        pass

    async def delete(self):
        """Deletes the data in the database (and the file itself, if applicable)."""
        pass

    async def get_user(self, username):
        """Gets a user from the database."""
        pass

    async def get_user_by_username(self, username):
        """Gets a user from the database by their username."""
        pass

    async def get_users(self):
        """Gets all users from the database."""
        pass

    async def create_user(self, username, hashed_password, role_id):
        """Creates a user and returns the user's ID."""
        pass

    async def delete_user(self, user_id):
        """Deletes a user."""
        pass

    async def change_user_role(self, user_id, new_role_id):
        """Change a user's role."""

    async def reset_users_roles(self, role_id):
        """Resets users' roles after a role has been deleted."""
        pass

    async def change_user_username(self, user_id, new_username):
        """Changes a user's username."""
        pass

    async def change_user_password(self, user_id, hashed_password):
        """Change a user's password."""
        pass

    async def get_file(self, file_id):
        """Gets a File by its file id."""
        pass

    async def get_file_by_id_or_filename(self, id_or_filename):
        """Gets a File by its id or filename."""
        pass

    async def get_files(self, *, user_id=None):
        """Gets all files or all files uploaded by a specific user."""
        pass

    async def get_file_count(self, *, user_id=None):
        """Gets the number of files uploaded total or by a specific user."""
        pass

    async def upload_file(self, file_id, filename, user_id):
        """Registers a file to the database.

        This does not include adding the file to the uploads folder."""
        pass

    async def delete_file(self, file_id):
        """Deletes a file from the database.

        This does not include deleting the file from the uploads folder.
        Returns whether or not the delete succeeded."""
        pass

    async def delete_files(self, user_id):
        """Deletes all files from a user and returns the filenames."""
        pass

    async def get_role(self, role_id):
        """Gets a role by its role id."""
        pass

    async def get_roles(self):
        """Gets all roles from the database."""
        pass

    async def create_role(self, name, permissions):
        """Creates a role in the database with a name and permissions."""
        pass

    async def delete_role(self, role_id):
        """Deletes a role from the database."""
        pass

    async def change_role_name(self, role_id, new_name):
        """Changes a role's name."""
        pass

    async def change_role_permissions(self, role_id, new_permissions):
        """Changes a role's permissions."""
        pass

    async def get_invite(self, invite):
        """Gets an invite from the database."""
        pass

    async def get_invites(self):
        """Gets all invites from the database."""
        pass

    async def create_invite(self, invite, user_id, max_uses, expires_at):
        """Creates an invite."""
        pass

    async def delete_invite(self, invite):
        """Deletes an invite."""
        pass

    async def increase_invite_uses(self, invite):
        pass

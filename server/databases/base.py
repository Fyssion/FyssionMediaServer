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

    async def get_file(self, file_id):
        """Gets a File by its file id."""
        pass

    async def get_file_by_id_or_filename(self, id_or_filename):
        """Gets a File by its id or filename."""
        pass

    async def get_files(self, *, user_id=None):
        """Gets all files or all files uploaded by a specific user"""
        pass

    async def upload_file(self, file_id, filename, user_id):
        """Registers a file to the database.

        This does not include adding the file to the uploads folder."""
        pass

    async def delete_file(self):
        """Deletes a file from the database.

        This does not include deleting the file from the uploads folder."""
        pass

    async def get_role(self, role_id):
        """Gets a role by its role id."""
        pass

    async def create_role(self, name, permissions):
        """Creates a role in the database with a name and permissions."""
        pass

    async def delete_role(self, role_id):
        """Deletes a role from the database."""
        pass

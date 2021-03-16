import asyncpg
from tornado.options import options

from .base import Database
from server.models import File, Invite, Permissions, Role, User


SCHEMA = """
SET TIME ZONE 'utc';

CREATE TABLE IF NOT EXISTS roles (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL UNIQUE,
    permissions INT NOT NULL,
    created_at TIMESTAMP DEFAULT (now() at time zone 'utc')
);

CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,

    username VARCHAR(100) NOT NULL UNIQUE,
    hashed_password VARCHAR(100) NOT NULL,

    role_id INT REFERENCES roles (id) ON DELETE NO ACTION ON UPDATE NO ACTION,

    created_at TIMESTAMP DEFAULT (now() at time zone 'utc')
);

CREATE TABLE IF NOT EXISTS files (
    id VARCHAR(30) PRIMARY KEY,
    filename TEXT NOT NULL,

    user_id INT NOT NULL REFERENCES users (id) ON DELETE NO ACTION ON UPDATE NO ACTION,
    views INT DEFAULT 0;

    uploaded_at TIMESTAMP DEFAULT (now() at time zone 'utc')
);

CREATE TABLE IF NOT EXISTS invites (
    id VARCHAR(10) PRIMARY KEY,

    uses INT DEFAULT 0,
    max_uses INT,

    user_id INT NOT NULL REFERENCES users (id) ON DELETE NO ACTION ON UPDATE NO ACTION,
    expires_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT (now() at time zone 'utc')
);
"""

DROP_TABLES = """
DROP TABLE invites;
DROP TABLE files;
DROP TABLE users;
DROP TABLE roles;
"""


class PostgresDatabase(Database):
    def __init__(self):
        super().__init__()
        self.pool = None

    async def prepare(self):
        self.pool = await asyncpg.create_pool(options.db_uri)

    async def close(self):
        await self.pool.close()

    async def is_initialized(self):
        try:
            await self.pool.fetchrow("SELECT 1 FROM files;")
        except asyncpg.UndefinedTableError:
            return False
        else:
            return True

    async def initialize(self, roles, admin):
        await self.pool.execute(SCHEMA)

        query = """INSERT INTO roles (name, permissions)
                   VALUES ($1, $2);
                """

        return_query = query.strip()[:-1] + "\nRETURNING roles.id;"

        # first role is the admin role. we need the ID of this role.
        admin_role = roles.pop(0)
        admin_role_id = await self.pool.fetchval(return_query, admin_role.name, admin_role.permissions.value)

        # we can now insert the other roles
        for role in roles:
            await self.pool.execute(query, role.name, role.permissions.value)

        # finally, we can insert the admin user with the admin role id
        query = """INSERT INTO users (username, hashed_password, role_id)
                   VALUES ($1, $2, $3);
                """

        await self.pool.execute(query, admin.username, admin.hashed_password, admin_role_id)

    async def delete(self):
        await self.pool.execute(DROP_TABLES)

    async def get_user(self, user_id):
        query = """SELECT *
                   FROM users
                   WHERE id=$1;
                """

        record = await self.pool.fetchrow(query, user_id)

        if not record:
            return None

        return User(
            id=record["id"],
            username=record["username"],
            hashed_password=record["hashed_password"],
            role_id=record["role_id"],
            created_at=record["created_at"],
            state=self.app,
        )

    async def get_user_by_username(self, username):
        query = """SELECT *
                   FROM users
                   WHERE username=$1;
                """

        record = await self.pool.fetchrow(query, username)

        if not record:
            return None

        return User(
            id=record["id"],
            username=record["username"],
            hashed_password=record["hashed_password"],
            role_id=record["role_id"],
            created_at=record["created_at"],
            state=self.app,
        )

    async def get_users(self):
        query = "SELECT * FROM users ORDER BY created_at ASC;"
        records = await self.pool.fetch(query)

        if not records:
            return []

        return [
            User(
                id=record["id"],
                username=record["username"],
                hashed_password=record["hashed_password"],
                role_id=record["role_id"],
                created_at=record["created_at"],
                state=self.app,
            )
            for record in records
        ]

    async def create_user(self, username, hashed_password, role_id):
        query = """INSERT INTO users (username, hashed_password, role_id)
                   VALUES ($1, $2, $3)
                   RETURNING id;
                """
        return await self.pool.fetchval(query, username, hashed_password, role_id)

    async def delete_user(self, user_id):
        query = "DELETE FROM users WHERE id=$1;"
        await self.pool.execute(query, user_id)

    async def change_user_role(self, user_id, new_role_id):
        query = """UPDATE users
                   SET role_id=$1
                   WHERE id=$2;
                """
        await self.pool.execute(query, new_role_id, user_id)

    async def reset_users_roles(self, role_id):
        query = """UPDATE users
                   SET role_id=$1
                   WHERE role_id=$2;
                """
        await self.pool.execute(query, 3, role_id)

    async def change_user_username(self, user_id, new_username):
        query = """UPDATE users
                   SET username=$1
                   WHERE id=$2;
                """
        await self.pool.execute(query, new_username, user_id)

    async def change_user_password(self, user_id, hashed_password):
        query = """UPDATE users
                   SET hashed_password=$1
                   WHERE id=$2;
                """
        await self.pool.execute(query, hashed_password, user_id)

    async def get_file(self, file_id):
        query = "SELECT * FROM files WHERE id=$1;"
        record = await self.pool.fetchrow(query, file_id)

        if not record:
            return None

        return File(
            id=record["id"],
            filename=record["filename"],
            user_id=record["user_id"],
            views=record["views"],
            uploaded_at=record["uploaded_at"],
            state=self.app,
            )

    async def get_file_by_id_or_filename(self, id_or_filename):
        query = "SELECT * FROM files WHERE id=$1 OR filename=$1;"
        record = await self.pool.fetchrow(query, id_or_filename)

        if not record:
            return None

        return File(
            id=record["id"],
            filename=record["filename"],
            user_id=record["user_id"],
            views=record["views"],
            uploaded_at=record["uploaded_at"],
            state=self.app,
            )

    async def get_files(self, *, user_id=None):
        if user_id:
            query = "SELECT * FROM files WHERE user_id=$1 ORDER BY uploaded_at DESC;"
            records = await self.pool.fetch(query, user_id)

        else:
            query = "SELECT * FROM files ORDER BY uploaded_at DESC;"
            records = await self.pool.fetch(query)

        if not records:
            return []

        return [
            File(
                id=record["id"],
                filename=record["filename"],
                user_id=record["user_id"],
                views=record["views"],
                uploaded_at=record["uploaded_at"],
                state=self.app,
                )
            for record in records
        ]

    async def get_file_count(self, *, user_id=None):
        if user_id:
            query = "SELECT COUNT(*) FROM files WHERE user_id=$1;;"
            return await self.pool.fetchval(query, user_id)

        else:
            query = "SELECT COUNT(*) FROM files;"
            return await self.pool.fetchval(query)

    async def increase_file_views(self, file_id):
        query = """UPDATE files
                   SET views = views + 1
                   WHERE id=$1;
                """
        await self.pool.execute(query, file_id)

    async def get_total_views(self, *, user_id=None):
        if user_id:
            query = "SELECT SUM(views) FROM files WHERE user_id=$1;;"
            return await self.pool.fetchval(query, user_id)

        else:
            query = "SELECT SUM(views) FROM files;"
            return await self.pool.fetchval(query)

    async def upload_file(self, file_id, filename, user_id):
        query = """INSERT INTO files (id, filename, user_id)
                   VALUES ($1, $2, $3);
                """
        await self.pool.execute(query, file_id, filename, user_id)

    async def delete_file(self, file_id):
        query = """DELETE FROM files
                   WHERE id=$1
                   RETURNING 1;
                """

        succeeded = await self.pool.fetchval(query, file_id)
        return bool(succeeded)

    async def delete_files(self, user_id):
        query = """DELETE FROM files
                   WHERE user_id=$1
                   RETURNING filename;
                """
        records = await self.pool.fetch(query, user_id)

        if not records:
            return []

        return [r[0] for r in records]

    async def get_role(self, role_id):
        """Gets a role by its role id."""
        query = "SELECT * FROM roles WHERE id=$1;"
        record = await self.pool.fetchrow(query, role_id)

        if not record:
            return None

        return Role(
            id=record["id"],
            name=record["name"],
            permissions=Permissions(record["permissions"]),
            created_at=record["created_at"],
            state=self.app,
        )

    async def get_roles(self):
        """Gets all roles from the database."""
        query = "SELECT * FROM roles ORDER BY created_at ASC;"
        records = await self.pool.fetch(query)

        if not records:
            return []

        return [
            Role(
                id=record["id"],
                name=record["name"],
                permissions=Permissions(record["permissions"]),
                created_at=record["created_at"],
                state=self.app,
            )
            for record in records
        ]

    async def create_role(self, name, permissions):
        query = """INSERT INTO roles (name, permissions)
                   VALUES ($1, $2)
                   RETURNING id;
                """
        return await self.pool.fetchval(query, name, permissions.value)

    async def delete_role(self, role_id):
        query = "DELETE FROM roles WHERE id=$1;"
        await self.pool.execute(query, role_id)

    async def change_role_name(self, role_id, new_name):
        query = """UPDATE roles
                   SET name=$1
                   WHERE id=$2;
                """
        await self.pool.execute(query, new_name, role_id)

    async def change_role_permissions(self, role_id, new_permissions):
        query = """UPDATE roles
                   SET permissions=$1
                   WHERE id=$2;
                """
        await self.pool.execute(query, new_permissions.value, role_id)

    async def get_invite(self, invite):
        query = "SELECT * FROM invites WHERE id=$1;"
        record = await self.pool.fetchrow(query, invite)

        if not record:
            return None

        return Invite(
            id=record["id"],
            uses=record["uses"],
            max_uses=record["max_uses"],
            user_id=record["user_id"],
            expires_at=record["expires_at"],
            created_at=record["created_at"],
            state=self.app,
        )

    async def get_invites(self):
        query = "SELECT * FROM invites ORDER BY created_at DESC;"
        records = await self.pool.fetch(query)

        if not records:
            return []

        return [
            Invite(
                id=record["id"],
                uses=record["uses"],
                max_uses=record["max_uses"],
                user_id=record["user_id"],
                expires_at=record["expires_at"],
                created_at=record["created_at"],
                state=self.app,
            )
            for record in records
        ]

    async def create_invite(self, invite, user_id, max_uses, expires_at):
        query = """INSERT INTO invites (id, user_id, max_uses, expires_at)
                   VALUES ($1, $2, $3, $4);
                """
        await self.pool.execute(query, invite, user_id, max_uses, expires_at)

    async def delete_invite(self, invite):
        query = "DELETE FROM invites WHERE id=$1;"
        await self.pool.execute(query, invite)

    async def increase_invite_uses(self, invite):
        query = "UPDATE invites SET uses = uses + 1 WHERE id=$1;"
        await self.pool.execute(query, invite)

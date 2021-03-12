from server.handlers.base import BaseHandler
from server.models.user import User


class APIHandler(BaseHandler):
    def get_response(self, status_code, data):
        data.setdefault("status_code", status_code)
        return data

    def _incorrect_auth(self):
        data = {
                "error": "INCORRECT_AUTHENTICATION",
                "info": "You provided incorrect authentication."
        }
        self.set_status(403)
        self.finish(self.get_response(403, data))

    async def authenticate_user(self):
        """Returns the User if the user is authenticated"""
        username = self.get_body_argument("username")
        password = self.get_body_argument("password")

        user = await self.db.get_user_by_username(username)

        if not user:
            self._incorrect_auth()
            return None

        password_matches = await user.check_password(password)

        if not password_matches:
            self._incorrect_auth()
            return None

        return user

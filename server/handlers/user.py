import tornado.web

from .base import BaseHandler


class LoginHandler(BaseHandler):
    async def get(self):
        if self.current_user:
            self.redirect(self.get_argument("next", "/"))
            return

        self.render("login.html", error=None)

    async def post(self):
        user = await self.db.get_user_by_username(self.get_argument("username"))

        if not user or not await user.check_password(self.get_argument("password")):
            self.render("login.html", error="Incorrect username or password.")
            return

        self.set_secure_cookie("fyssionmediaserver_user", str(user.id))
        self.redirect(self.get_argument("next", "/"))


class LogoutHandler(BaseHandler):
    async def get(self):
        self.clear_cookie("fyssionmediaserver_user")
        self.redirect(self.get_argument("next", "/"))


class ProfileHandler(BaseHandler):
    @tornado.web.authenticated
    async def get(self):
        self.render("profile.html", error=None)

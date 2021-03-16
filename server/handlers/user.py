import tornado.web

from .base import BaseHandler
from server.models import User


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
    async def render_profile(self, *, message=None, data={}):
        files_uploaded = await self.db.get_file_count(user_id=self.current_user.id)
        self.render("profile.html", files_uploaded=files_uploaded, message=message, data=data)

    @tornado.web.authenticated
    async def get(self):
        await self.render_profile()

    @tornado.web.authenticated
    async def post(self):
        action = self.get_argument("action")

        if action == "changeUsername":
            username = self.get_body_argument("username")
            password = self.get_body_argument("password")

            if not await self.current_user.check_password(password):
                await self.render_profile(data={"changeusername_incorrect_pass": True, "username": username})
                return

            already_exists = await self.db.get_user_by_username(username)

            if already_exists:
                await self.render_profile(data={"username_exists_error": True, "username": username})
                return

            await self.current_user.change_username(username)
            await self.render_profile(message=("success", "Successfully updated username."))

        elif action == "changePassword":
            old_password = self.get_body_argument("oldPassword")
            new_password = self.get_body_argument("newPassword")
            confirm_password = self.get_body_argument("confirmPassword")

            if new_password != confirm_password:
                await self.render_profile(data={"pass_not_match": True})
                return

            if not await self.current_user.check_password(old_password):
                await self.render_profile(data={"changepassword_incorrect_pass": True})
                return

            await self.current_user.change_password(new_password)
            await self.render_profile(message=("success", "Successfully updated password."))

        elif action == "deleteAccount":
            if self.current_user.id == 1:
                await self.render_profile(message=("danger", "The Admin user cannot be deleted."))
                return

            if self.get_argument("username") != self.current_user.username:
                await self.return_profile(message=("danger", "Incorrect username. Please type the correct username."))
                return

            await self.current_user.delete()
            self.clear_cookie("fyssionmediaserver_user")
            self.redirect("/login")

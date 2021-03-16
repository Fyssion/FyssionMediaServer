import tornado.web

from .base import BaseHandler
from server.models import User


class InviteHandler(BaseHandler):
    async def get(self, invite):
        self.redirect(f"/signup?invite={invite}")


class SignupHandler(BaseHandler):
    async def get(self):
        invite_id = self.get_argument("invite", None)

        if not invite_id:
            raise tornado.web.HTTPError(403)

        invite = await self.db.get_invite(invite_id)

        if not invite:
            self.render("invalid_invite.html")
            return

        if not invite.is_valid():
            print("here")
            self.render("invalid_invite.html")
            await invite.delete()
            return

        self.render("signup.html", invite=invite, error=None, data={})

    async def post(self):
        invite_id = self.get_argument("invite", None)

        if not invite_id:
            raise tornado.web.HTTPError(403)

        invite = await self.db.get_invite(invite_id)

        if not invite:
            self.render("invalid_invite.html")
            return

        if not invite.is_valid():
            self.render("invalid_invite.html")
            await invite.delete()
            return

        username = self.get_body_argument("username")
        password = self.get_body_argument("password")
        confirm_password = self.get_body_argument("confirm-password")

        if password != confirm_password:
            self.render("signup.html", invite=invite, error=None, data={"pass_match_error": True, "username": username})
            return

        already_exists = await self.db.get_user_by_username(username)

        if already_exists:
            self.render("signup.html", invite=invite, error=None, data={"username_exists_error": True, "username": username})
            return

        user = await User.create(username, password, self.application)

        if (invite.uses + 1) == invite.max_uses:
            await invite.delete()

        await invite.increase_uses()

        self.set_secure_cookie("fyssionmediaserver_user", str(user.id))
        self.current_user = user
        await self.current_user.get_role()
        self.render("setup.html", created=True, password=password)


class SetupHandler(BaseHandler):
    @tornado.web.authenticated
    async def get(self):
        self.render("confirm_password.html")

    @tornado.web.authenticated
    async def post(self):
        self.render("setup.html", created=False, password=self.get_body_argument("password"))

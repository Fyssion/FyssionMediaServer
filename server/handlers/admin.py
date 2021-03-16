import datetime

import tornado.ioloop
import tornado.web

from .base import BaseHandler
from server.models import Invite, Permissions, Role
from server.utils import checks


class SettingsHandler(BaseHandler):
    TABS = {
            "users": "settings/users.html",
            "roles": "settings/roles.html",
            "invites": "settings/invites.html",
        }

    @tornado.web.authenticated
    async def get(self):
        tab = self.get_argument("tab", "users").lower()

        if tab not in self.TABS.keys():
            tab = "users"

        perms = self.current_user.role.permissions
        if not (perms.edit_settings or perms.manage_invites):
            raise tornado.web.HTTPError(403)

        elif not perms.edit_settings and perms.manage_invites:
            tab = "invites"

        elif perms.edit_settings and not perms.manage_invites:
            if tab == "invites":
                tab = "users"

        context = {}

        if tab == "users":
            users = await self.db.get_users()
            roles = await self.db.get_roles()

            for user in users:
                await user.get_role()

            context.update({"users": users, "roles": roles})

        elif tab == "roles":
            roles = await self.db.get_roles()

            full_roles = []

            for role in roles:
                # format the permissions in a pretty way
                # each permission is a tuple: ("perm_name", True/False)
                permissions = ", ".join(
                    p[0].replace("_", " ")
                    for p in role.permissions
                    if p[1]
                )
                full_roles.append((role, permissions))

            all_permissions = list(Permissions.VALID_FLAGS.keys())

            context["roles"] = full_roles
            context["all_permissions"] = all_permissions

        elif tab == "invites":
            invites = await self.db.get_invites()

            to_remove = []

            for i, invite in enumerate(invites):
                if not invite.is_valid():
                    tornado.ioloop.IOLoop.current().add_callback(invite.delete)
                    to_remove.append(i)

                await invite.get_user()

            for i in to_remove:
                invites.pop(i)

            context["invites"] = invites

        template = self.TABS.get(tab)
        self.render(template, tab=tab, message=None, **context)

    @tornado.web.authenticated
    async def post(self):
        tab = self.get_argument("tab")

        if not tab:
            raise tornado.web.HTTPError(400)

        if tab not in self.TABS.keys():
            raise tornado.web.HTTPError(400)

        perms = self.current_user.role.permissions
        if not (perms.edit_settings or perms.manage_invites):
            raise tornado.web.HTTPError(403)

        action = self.get_argument("action")

        if not action:
            raise tornado.web.HTTPError(400)

        if action == "changeRole":
            if not perms.edit_settings:
                raise tornado.web.HTTPError(403)

            user_id = self.get_body_argument("userid")
            role_id = self.get_body_argument("roleid")

            if not all((user_id, role_id)):
                raise tornado.web.HTTPError(400)

            if int(user_id) == 1:
                self.render("/settings?tab=users", tab=tab, message=("danger", "That user cannot be changed."))
                return

            user = await self.db.get_user(int(user_id))
            await user.change_role(int(role_id))

        elif action == "deleteUser":
            if not perms.edit_settings:
                raise tornado.web.HTTPError(403)

            user_id = self.get_body_argument("userid")

            if not user_id:
                raise tornado.web.HTTPError(400)

            if int(user_id) == 1:
                self.render("/settings?tab=roles", tab=tab, message=("danger", "That user cannot be deleted."))
                return

            user = await self.db.get_user(int(user_id))
            await user.delete()

        elif action == "changeRoleName":
            if not perms.edit_settings:
                raise tornado.web.HTTPError(403)

            role_id = self.get_body_argument("roleid")
            new_name = self.get_body_argument("rolename")

            role = await self.db.get_role(int(role_id))
            await role.change_name(new_name)

        elif action == "changeRolePerms":
            if not perms.edit_settings:
                raise tornado.web.HTTPError(403)

            role_id = self.get_body_argument("roleid")

            if int(role_id) == 1:
                self.render("/settings?tab=roles", tab=tab, message=("danger", "That role's permissions cannot be changed."))
                return

            new_perms = {}

            for perm in Permissions.VALID_FLAGS.keys():
                new_perms[perm] = bool(self.get_body_argument(perm, False))

            role = await self.db.get_role(int(role_id))
            await role.change_permissions(Permissions(**new_perms))

        elif action == "createRole":
            if not perms.edit_settings:
                raise tornado.web.HTTPError(403)

            role_name = self.get_body_argument("rolename")
            perms = {}

            for perm in Permissions.VALID_FLAGS.keys():
                perms[perm] = bool(self.get_body_argument(perm, False))

            await Role.create(role_name, Permissions(**perms), self.application)

        elif action == "deleteRole":
            if not perms.edit_settings:
                raise tornado.web.HTTPError(403)

            role_id = self.get_body_argument("roleid")

            if int(role_id) in (1, 3):
                self.render("/settings?tab=roles", tab=tab, message=("danger", "That role cannot be deleted."))
                return

            role = await self.db.get_role(int(role_id))
            await role.delete()

        elif action == "createInvite":
            if not perms.manage_invites:
                raise tornado.web.HTTPError(403)

            max_uses = self.get_body_argument("maxuses")
            expires_in = self.get_body_argument("expires")

            if max_uses == "null":
                max_uses = None
            else:
                max_uses = int(max_uses)

            if expires_in == "null":
                expires_in = None
            else:
                expires_in = datetime.datetime.utcnow() + datetime.timedelta(seconds=int(expires_in))

            await Invite.create(self.current_user, max_uses, expires_in, self.application)

        elif action == "deleteInvite":
            if not perms.manage_invites:
                raise tornado.web.HTTPError(403)

            invite_id = self.get_body_argument("invite")

            if not invite_id:
                raise tornado.web.HTTPError(400)

            invite = await self.db.get_invite(invite_id)

            if not invite:
                raise tornado.web.HTTPError(400)

            await invite.delete()

        self.redirect(f"/settings?tab={tab}")


class InvitesHandler(BaseHandler):
    async def get(self):
        pass

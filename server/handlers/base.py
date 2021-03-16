import tornado.web
import traceback


class BaseHandler(tornado.web.RequestHandler):
    async def prepare(self):
        user_id = self.get_secure_cookie("fyssionmediaserver_user")
        if user_id:
            self.current_user = await self.db.get_user(int(user_id))
            if self.current_user:
                await self.current_user.get_role()

    def write_error(self, status_code, **kwargs):
        if status_code == 404:
            self.render("errors/404.html")

        elif self.settings.get("serve_traceback") and "exc_info" in kwargs:
            # in debug mode, try to send a traceback
            exc = traceback.format_exception(*kwargs["exc_info"])
            self.render("errors/traceback.html", traceback=exc)
        else:
            self.render("errors/any.html", code=status_code, reason=self._reason)

    @property
    def db(self):
        return self.application.db

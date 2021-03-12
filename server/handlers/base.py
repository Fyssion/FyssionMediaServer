import tornado.web


class BaseHandler(tornado.web.RequestHandler):
    async def prepare(self):
        user_id = self.get_secure_cookie("fyssionmediaserver_user")
        if user_id:
            self.current_user = await self.db.get_user(int(user_id))

    @property
    def db(self):
        return self.application.db

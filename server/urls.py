from . import handlers

handler_urls = [
    # Home page
    (r"/", handlers.home.HomeHandler),
    (r"/upload", handlers.home.UploadHandler),

    # User pages
    (r"/login", handlers.user.LoginHandler),
    (r"/logout", handlers.user.LogoutHandler),
    (r"/profile", handlers.user.ProfileHandler),

    # Setup pages
    (r"/invite/(.*)", handlers.invite.InviteHandler),
    (r"/signup", handlers.invite.SignupHandler),
    (r"/setup", handlers.invite.SetupHandler),

    # Media viewer
    (r"/file/(.*)/delete", handlers.file.FileDeleteHandler),
    (r"/file/(.*)", handlers.file.FileHandler),

    # Admin pages
    (r"/settings", handlers.admin.SettingsHandler),
    (r"/invites", handlers.admin.InvitesHandler),

    # API
    (r"/api/files", handlers.api.files.FilesHandler),
    (r"/api/downloads", handlers.api.downloads.DownloadsHandler),

    # File handler
    (r"/(.*)", handlers.static.UploadFileHandler, {"path": "server/static/uploads"}),
]

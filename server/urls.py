from . import handlers

handler_urls = [
    # Home page
    (r"/", handlers.home.HomeHandler),
    (r"/upload", handlers.home.UploadHandler),

    # User pages
    (r"/login", handlers.user.LoginHandler),
    (r"/logout", handlers.user.LogoutHandler),
    (r"/profile", handlers.user.ProfileHandler),

    # Media viewer
    (r"/file/(.*)", handlers.file.FileHandler),
    (r"/file/(.*)/delete", handlers.file.FileDeleteHandler),


    # Admin page
    (r"/admin", handlers.admin.AdminHandler),

    # API
    (r"/api/files", handlers.api.files.FilesHandler),

    # File handler
    (r"/(.*)", handlers.static.UploadFileHandler, {"path": "server/static/uploads"}),
]

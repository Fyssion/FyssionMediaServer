import functools
import urllib.parse

import tornado.web

from server.models import Permissions


def has_permissions(**perms):
    """Decorator similar to `tornado.web.authenticated` that checks if a user has valid permissions"""

    invalid = set(perms) - set(Permissions.VALID_FLAGS)
    if invalid:
        raise TypeError(f"Invalid permission(s): {', '.join(invalid)}")

    def predicate(method):
        @functools.wraps(method)
        def wrapper(self, *args, **kwargs):
            if not self.current_user:
                if self.request.method in ("GET", "HEAD"):
                    url = self.get_login_url()
                    if "?" not in url:
                        if urllib.parse.urlsplit(url).scheme:
                            # if login url is absolute, make next absolute too
                            next_url = self.request.full_url()
                        else:
                            assert self.request.uri is not None
                            next_url = self.request.uri
                        url += "?" + urllib.parse.urlencode(dict(next=next_url))
                    self.redirect(url)
                    return None
                raise tornado.web.HTTPError(403)

            if self.current_user:
                permissions = self.current_user.role.permissions
                missing = [perm for perm, value in perms.items() if getattr(permissions, perm) != value]

                if missing:
                    raise tornado.web.HTTPError(403)

            return method(self, *args, **kwargs)

        return wrapper
    return predicate

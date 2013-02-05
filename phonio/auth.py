from tornado.web import asynchronous, RequestHandler, HTTPError
from tornado.auth import GoogleMixin
from tornado.escape import json_encode, json_decode

from phonio import config

cfg = config.settings("settings.cfg", "phonio")
AUTHORIZED_DOMAINS = cfg.authorized_domains.split(',')

class RestrictedHandler(RequestHandler):
    def get_current_user(self):
        user_json = self.get_secure_cookie("user")
        if not user_json: return None
        return json_decode(user_json)

class LoginHandler(RestrictedHandler):
    def get(self):
        return self.render("login.html")

class LogoutHandler(RestrictedHandler):
    def get(self):
        self.clear_all_cookies()
        return self.render("logout.html")

class AuthenticateHandler(RequestHandler, GoogleMixin):
    @asynchronous
    def get(self):
        if self.get_argument("openid.mode", None):
            self.get_authenticated_user(self.async_callback(self._on_auth))
            return
        self.authenticate_redirect()

    def _on_auth(self, user):
        if not user:
            raise HTTPError(500, "Google auth failed")

        domain = user["email"].split('@')[-1]
        if domain not in AUTHORIZED_DOMAINS:
            raise HTTPError(403)

        self.set_secure_cookie("user", json_encode(user))
        next_url = self.get_argument("next", "/")
        self.redirect(next_url)

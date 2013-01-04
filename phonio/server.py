import os

import tornado.ioloop
from tornado.web import RedirectHandler, Application

from phonio import softphone, auth
from phonio import config

if __name__ == '__main__':
    args = config.args()
    cfg = config.settings("settings.cfg", "phonio")

    root = os.path.dirname(__file__)
    settings = { "template_path": os.path.join(root, "templates"),
            "login_url": "/authenticate",
            "debug": args.debug,
            "cookie_secret": cfg.cookie_secret }

    app = Application([
            (r'/', RedirectHandler, {"url": "/phones"}),
            (r'/login', auth.LoginHandler),
            (r'/logout', auth.LogoutHandler),
            (r'/authenticate', auth.AuthenticateHandler),

            (r'/phones', softphone.PhonesHandler),
            (r'/phones/(.*)', softphone.PhoneHandler),
            (r'/voice', softphone.VoiceHandler),
            (r'/status', softphone.StatusHandler),

            (r'/static/(.*)', tornado.web.StaticFileHandler, dict(path=os.path.join(root, "assets"))),
        ], **settings)

    app.listen(args.port, xheaders=True)
    tornado.ioloop.IOLoop.instance().start()

import json

from tornado.web import RequestHandler, asynchronous
from tornado.httpclient import AsyncHTTPClient
from tornado.curl_httpclient import CurlAsyncHTTPClient
from tornado import gen

from phonio import config

URL_CONFIG = config.settings("settings.cfg", "url")

AsyncHTTPClient.configure(CurlAsyncHTTPClient)


class Rooming(RequestHandler):

    def initialize(self, fetcher=None):
        self.fetcher = fetcher

    @asynchronous
    @gen.engine
    def post(self):
        """initiating a conference room"""
        phonables = self.get_arguments("phonables")
        res = None
        for phid in phonables:
            res = yield gen.Task(self.fetcher.fetch,
                                 URL_CONFIG.phonable_url + "/" + phid)
        self.set_status(res.code)
        body = {"number": json.loads(res.body)["number"]}
        self.finish(body)

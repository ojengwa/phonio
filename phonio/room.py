import json

from tornado.web import RequestHandler, asynchronous
from tornado.httpclient import AsyncHTTPClient
from tornado.curl_httpclient import CurlAsyncHTTPClient
from tornado import gen

from phonio import config

URL_CONFIG = config.settings("settings.cfg", "url")

AsyncHTTPClient.configure(CurlAsyncHTTPClient)

def phonable_path(phid):
    return URL_CONFIG.phonable_url + '/' + phid

class Rooming(RequestHandler):

    def initialize(self, fetcher=None):
        self.fetcher = fetcher or AsyncHTTPClient()

    @asynchronous
    @gen.engine
    def post(self):
        """initiating a conference room"""
        phonables = self.get_arguments("phonables")
        results = yield [gen.Task(self.fetcher.fetch, phonable_path(phid))
                         for phid in phonables]
        self.set_status(results[0].code) #TODO remove me
        numbers = [json.loads(r.body)["number"] for r in results]
        body = {"numbers": numbers}
        self.finish(body)

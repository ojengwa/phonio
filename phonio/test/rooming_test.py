import json
import unittest
from mock import patch, Mock, MagicMock
from urllib import urlencode

from tornado.gen import YieldPoint, Task
from tornado.ioloop import IOLoop
from tornado.web import Application, RequestHandler
from tornado.httpclient import AsyncHTTPClient, HTTPResponse
from tornado.testing import AsyncHTTPTestCase, LogTrapTestCase

from phonio.room import Rooming

class RoomingTest(AsyncHTTPTestCase, LogTrapTestCase):
    def get_app(self):
        self.fetcher = AsyncHTTPClient()
        return Application([
            (r"/rooms", Rooming, {"fetcher": self.fetcher}),
            ])

    def get_new_ioloop(self):
        return IOLoop.instance()

    def test_post_phonable_ids(self):
        attrs = { "get_result.return_value": MagicMock(code=200) }
        with patch("phonio.room.gen.Task", spec=YieldPoint, **attrs) as task:
            # payload = urlencode([('phonables', 'abc'), ('phonables', 'def')])
            payload = urlencode([('phonables', 'abc')])
            res = self.fetch("/rooms", method="POST", body=payload)

            self.assertEqual(res.code, 200)
            # task.assert_called_once_with('foo')

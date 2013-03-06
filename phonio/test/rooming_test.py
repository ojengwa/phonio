import json
import unittest
from mock import patch, Mock, MagicMock
from urllib import urlencode

from tornado.gen import YieldPoint
from tornado.web import Application, RequestHandler
from tornado.httpclient import AsyncHTTPClient
from tornado.testing import AsyncHTTPTestCase, LogTrapTestCase

from phonio.room import Rooming

class RoomingTest(AsyncHTTPTestCase, LogTrapTestCase):
    def get_app(self):
        assert self.io_loop
        return Application([
            (r"/rooms", Rooming, {"fetcher": AsyncHTTPClient()}),
            ])

    @patch("tornado.gen.Task")
    def test_post_phonable_ids(self, task):
        # payload = urlencode([('phonables', 'abc'), ('phonables', 'def')])
        payload = urlencode([('phonables', 'abc')])
        task.return_value = MagicMock(spec=YieldPoint)
        task.is_ready.return_value = True
        task.get_result.return_value = "123"
        res = self.fetch("/rooms", method="POST", body=payload)
        self.assertEqual(res.code, 200)
        self.assertEqual(res.body, json.dumps(['abc', 'def']))

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
        return Application([(r"/rooms", Rooming)])

    def get_new_ioloop(self):
        return IOLoop.instance()

    def test_post_phonable_ids(self):
        result = MagicMock(code=200)
        result.body = json.dumps({"number": "+13103004000"})
        attrs = {"get_result.return_value": result}
        with patch("phonio.room.gen.Task", spec=YieldPoint, **attrs) as task:
            payload = urlencode([('phonables', 'abc'), ('phonables', 'def')])
            # payload = urlencode([('phonables', 'abc')])
            res = self.fetch("/rooms", method="POST", body=payload)

            self.assertEqual(res.code, 200)
            self.assertEqual(json.loads(res.body)['number'], '+13103004000')
            # task.assert_called_once_with('foo')

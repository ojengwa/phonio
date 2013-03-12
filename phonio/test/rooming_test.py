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


def phonable_task(func, url):
    number = '+12103004000' if url.endswith('abc') else '+13103004000'
    reply = MagicMock()
    reply.code = 200
    reply.body = json.dumps({"number": number})

    task = MagicMock(spec=YieldPoint)
    task.get_result.return_value = reply
    return task

class RoomingTest(AsyncHTTPTestCase, LogTrapTestCase):
    def get_app(self):
        return Application([(r"/rooms", Rooming)])

    def get_new_ioloop(self):
        return IOLoop.instance()

    @patch("phonio.room.gen.Task", side_effect=phonable_task)
    def test_post_phonable_ids(self, task):
        payload = urlencode([('phonables', 'abc'), ('phonables', 'def')])
        res = self.fetch("/rooms", method="POST", body=payload)

        self.assertEqual(res.code, 200)
        self.assertEqual(json.loads(res.body)['numbers'],
                         ['+12103004000', '+13103004000'])

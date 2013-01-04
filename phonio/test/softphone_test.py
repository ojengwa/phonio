import os
import unittest
import xml.etree.ElementTree as ET
from urllib import urlencode

from mock import Mock, MagicMock, patch, PropertyMock
from tornado.escape import json_encode, json_decode
from tornado.testing import AsyncHTTPTestCase, LogTrapTestCase
from tornado.web import Application

from phonio.softphone import Rolodex, VoiceHandler, StatusHandler, dial, PhoneHandler


class RolodexTest(LogTrapTestCase):
    def setUp(self):
        handler = MagicMock(name="handler")
        self.rolodex = Rolodex(handler)
        self.rolodex.client = Mock(name="twilio client")

    def test_numbers_from_cookie(self):
        self.rolodex.handler.get_secure_cookie.return_value = json_encode(["+13003004000"])
        self.assertEqual(self.rolodex.numbers(), ["+13003004000"])
        self.rolodex.handler.get_secure_cookie.assert_called_with("numbers")

    def test_numbers_from_twilio(self):
        self.rolodex.handler.get_secure_cookie.return_value = None
        self.rolodex.handler.current_user.__getitem__.return_value = "bruce@lee.com"

        from collections import namedtuple
        Number = namedtuple("Phone", "email, phone_number")
        n1 = Number(email="bruce@lee.com", phone_number="+13003004002")
        n2 = Number(email="bruce@lee.com", phone_number="+13003004003")
        n3 = Number(email="bruce@lee.com", phone_number="+13003004001")
        self.rolodex.client.phone_numbers.list.return_value = [n1, n2, n3]

        self.assertEqual(self.rolodex.numbers(), ["+13003004001", "+13003004002", "+13003004003"])
        self.rolodex.client.phone_numbers.list.assert_called_with(friendly_name="bruce@lee.com")
        self.assertEqual(self.rolodex.get_name("+13003004001"), "ace")

    def test_get_name(self):
        numbers = Mock()
        numbers.return_value = ["+13003004001", "+13003004002", "+13003004003"]
        self.rolodex.numbers = numbers
        self.assertEqual(self.rolodex.get_name("+13003004001"), "ace")
        self.assertEqual(self.rolodex.get_name("+13003004002"), "bruce")
        self.assertEqual(self.rolodex.get_name("+13003004003"), "carl")

    def test_get_number(self):
        numbers = Mock()
        numbers.return_value = ["+13003004001", "+13003004002", "+13003004003"]
        self.rolodex.numbers = numbers
        self.assertEqual(self.rolodex.get_number('ace'), "+13003004001")

    def test_names(self):
        self.assertEqual(self.rolodex.names, ['ace', 'bruce', 'carl', 'dan', 'eli', 'frank'])

class DialTest(LogTrapTestCase):
    def test_dial(self):
        body = dial("+13003004002", "+13003004001")
        tree = ET.fromstring(body)
        self.assertEqual(tree.find(".//Dial/Client").text, '+13003004002')

class VoiceHandlerTest(AsyncHTTPTestCase, LogTrapTestCase):
    def get_app(self):
        return Application([(r'/voice', VoiceHandler)])

    def test_post(self):
        with patch("phonio.softphone.dial") as dial:
            dial.return_value = "mock"
            res = self.fetch('/voice', method='POST', body=urlencode({"From": "+13003004001", "Called": "+13003004002"}))
            dial.assert_called_once_with("+13003004002", "+13003004001")

class StatusHandlerTest(AsyncHTTPTestCase, LogTrapTestCase):
    def get_app(self):
        return Application([(r'/status', StatusHandler)])

    def test_post(self):
        res = self.fetch('/status', method='POST', body="")
        tree = ET.fromstring(res.body)
        self.assertIsNotNone(tree.find(".//Hangup"))

class PhoneHandlerTest(LogTrapTestCase):
    @patch('phonio.softphone.PhoneHandler.current_user', new_callable=PropertyMock, spec=True)
    def test_get(self, current_user):
        app = MagicMock()
        request = MagicMock()
        handler = PhoneHandler(app, request)
        handler.rolodex = Mock()
        handler.render = Mock()
        handler.rolodex.get_number.return_value = "+13003004000"

        handler.get('ace')
        current_user.assert_called_with()
        handler.rolodex.get_number.assert_called_with("ace")

        kwargs = handler.render.call_args[1]
        self.assertEqual(kwargs["number"], "+13003004000")
        self.assertEqual(kwargs["name"], "ace")
        self.assertIsNotNone(kwargs["pp_phone"])
        self.assertIsNotNone(kwargs["device_token"])

if __name__ == '__main__':
    unittest.main()

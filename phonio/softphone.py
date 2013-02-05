from operator import attrgetter

from tornado.web import authenticated, RequestHandler
from tornado.escape import json_encode, json_decode
import twilio.twiml
from twilio.rest import TwilioRestClient
from twilio.util import TwilioCapability

from phonio.auth import RestrictedHandler
from phonio import config
from phonio import util

URL_CONFIG = config.settings("settings.cfg", "url")
TWILIO_CONFIG = config.settings("settings.cfg", "twilio")


class Rolodex(object):
    def __init__(self, handler):
        self.handler = handler
        self.client = TwilioRestClient(TWILIO_CONFIG.account_sid, TWILIO_CONFIG.auth_token)
        self.names = ['ace', 'bruce', 'carl', 'dan', 'eli', 'frank']

    def numbers(self):
        numbers_json = self.handler.get_secure_cookie("numbers")
        if not numbers_json:
            email = self.handler.current_user["email"]
            phone_numbers = self.client.phone_numbers.list(friendly_name=email)
            phone_numbers = sorted(phone_numbers, key=attrgetter('phone_number'))
            numbers = [n.phone_number for n in phone_numbers]
            self.handler.set_secure_cookie("numbers", json_encode(numbers))
            return numbers
        return json_decode(numbers_json)

    def get_name(self, number):
        if not hasattr(self, "_numbers_to_names"):
            self._numbers_to_names = dict(zip(self.numbers(), self.names))
        return self._numbers_to_names[number]

    def get_number(self, name):
        if not hasattr(self, "_names_to_numbers"):
            self._names_to_numbers = dict(zip(self.names, self.numbers()))
        return self._names_to_numbers[name]

class RolodexHandler(RestrictedHandler):
    def initialize(self):
        self.rolodex = Rolodex(self)

class PhonesHandler(RolodexHandler):
    @authenticated
    def get(self):
        self.render("phones.html", rolodex=self.rolodex)

class PhoneHandler(RolodexHandler):
    @authenticated
    def get(self, name):
        capability = TwilioCapability(TWILIO_CONFIG.account_sid, TWILIO_CONFIG.auth_token)
        number = self.rolodex.get_number(name)
        uniq_client_name = number
        capability.allow_client_incoming(uniq_client_name)
        self.render("phone.html",
                device_token=capability.generate(),
                pp_phone=util.pp_phone,
                name=name,
                number=number)

def dial(client_name, caller_id):
    resp = twilio.twiml.Response()
    with resp.dial(callerId=caller_id, action=URL_CONFIG.status) as r:
        r.client(client_name)
    return str(resp)

class VoiceHandler(RequestHandler):
    def post(self):
        client_name = self.get_argument("Called")
        caller_id = self.get_argument("From")
        self.finish(dial(client_name, caller_id))

class StatusHandler(RequestHandler):
    def post(self):
        resp = twilio.twiml.Response()
        resp.hangup()
        self.finish(str(resp))

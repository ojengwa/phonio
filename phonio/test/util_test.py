import unittest

from phonio import util


class UtilTest(unittest.TestCase):
    def test_phone_number_formatter(self):
        number = util.pp_phone("+12133004000")
        self.assertEqual(number, "213-300-4000")

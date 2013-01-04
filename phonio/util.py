import pprint
import re

pp = pprint.PrettyPrinter(indent=4)

def log(obj):
    print "\n**********************************************************************"
    pp.pprint(obj)
    print "**********************************************************************\n"

def pp_phone(number):
    matched = re.match(r".*(\d{3})(\d{3})(\d{4})$", number)
    if matched:
        return "{}-{}-{}".format(*matched.groups())
    return number

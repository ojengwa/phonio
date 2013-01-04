import os
import argparse
from ConfigParser import ConfigParser

def args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--debug", action="store_true", help="start the server in debugging mode")
    parser.add_argument("--port", default="4000")
    return parser.parse_args()

class _Setting:
    def __init__(self, settings):
        for key, value in settings:
            setattr(self, key, value)

def settings(filename, section):
    cfg = ConfigParser()
    cfg.read(os.path.join(os.path.dirname(__file__), "..", filename))
    return _Setting(cfg.items(section))

#!/usr/bin/env python

import subprocess, signal, sys, os
import datetime

def handler(signum, frame):
    sys.exit(0)

def clear():
    subprocess.call(["clear"])

def main():
    while True:
        pipe = os.open('triggertest.pipe', os.O_RDONLY)
        clear()
        finput = os.fdopen(pipe)
        line = finput.readline()
        subprocess.call(['python', '-m',
                'tornado.testing',  'phonio.test.rooming_test'])
        finput.close()
        print datetime.datetime.now()


signal.signal(signal.SIGINT, handler)

if __name__ == '__main__':
    main()

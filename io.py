import sys

import decoder

def message(s):
    s = decoder.encode(s)
    if s[-1] != '\n':
        s += '\n'
    sys.stderr.write(s)
    sys.stderr.flush()

def output(s):
    s = decoder.encode(s)
    if s[-1] != '\n':
        s += '\n'
    sys.stdout.write(s)
    sys.stdout.flush()

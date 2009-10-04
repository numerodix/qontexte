import re

from lib import chardet
from lib.chardet import universaldetector

import io

class Detector(object):
    def __init__(self, txt_byte=None, filename=None):
        self.txt_byte = txt_byte
        self.filename = filename

    def detect_in_html(self):
        txt_byte = self.txt_byte
        if self.filename:
            txt_byte = open(self.filename, 'r').read(1000)
        match = re.search(u'(?is)[<]meta[^>]*charset[ ]*=[ "\']*([\-a-zA-Z0-9]+)',
                          txt_byte)
        if match:
            return match.group(1)

    def detect_in_xml(self):
        txt_byte = self.txt_byte
        if self.filename:
            txt_byte = open(self.filename, 'r').read(300)
        match = re.search(u'(?is)[<]?xml[^>]*encoding[ ]*=[ "\']*([\-a-zA-Z0-9]+)',
                          txt_byte)
        if match:
            return match.group(1)

    def detect_with_chardet(self):
        len_limit = 500*1024
        dct = {}
        if self.txt_byte:
            dct = chardet.detect(self.txt_byte[:len_limit])
        else:
            f = open(self.filename, 'r')
            detector = universaldetector.UniversalDetector()
            numbytes = 0
            for line_byte in f.xreadlines():
                detector.feed(line_byte)
                numbytes += len(line_byte)
                if detector.done: break
                if numbytes > len_limit: break # don't read forever
            detector.close()
            dct = detector.result
        return dct.get('encoding')


def detect_encoding(txt_byte=None, filename=None):
    if not txt_byte and not filename:
        raise Exception("No argument given")

    detector = Detector(txt_byte=txt_byte, filename=filename)
    for method in ('detect_in_html', 'detect_in_xml', 'detect_with_chardet'):
        encoding = getattr(detector, method).__call__()
        if encoding:
            encoding = encoding.lower()
            break

    # print debug notice
    debug_lines=5; linelen=74
    length = linelen * debug_lines
    txt_byte = txt_byte or open(filename, 'r').read(length)
    debug_s = ''
    fragment = re.sub('\s', ' ', txt_byte[:length])
    for i in range(debug_lines):
        if fragment:
            debug_s += "  |%s|" % fragment[:linelen]
            fragment = fragment[linelen:]
            if fragment: debug_s += '\n'
    io.message("Detected encoding %s for...\n%s" % (encoding, debug_s))

    return encoding or 'utf-8'

def encode(txt, encoding='utf-8'):
    """Allow recovery if given a bytestring"""
    if isinstance(txt, unicode):
        return txt.encode(encoding)
    return txt

def decode(txt, encoding):
    """Allow recovery if given a unicode string"""
    if not isinstance(txt, unicode):
        return txt.decode(encoding)
    return txt

def detect_decode(txt_byte):
    encoding = detect_encoding(txt_byte=txt_byte)
    txt_u = txt_byte.decode(encoding)
    return txt_u


if __name__ == "__main__": 
    import sys
    print detect_encoding(filename=sys.argv[1])
    sys.exit()

    txt_byte = open(sys.argv[1], 'r').read()
    print detect_encoding(txt_byte)


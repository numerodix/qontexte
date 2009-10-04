#!/usr/bin/env python

import re
import sys

from filters import html
from filters import mediawiki

def unhtml(txt_u):
    filter_html = html.HtmlFilter()
    txt_u = filter_html.unmarkup(txt_u)
    return txt_u

def get_wiki_body(txt_u):
    filter_mediawiki = mediawiki.MediawikiFilter()
    txt_u = filter_mediawiki.get_wiki_body(txt_u)
    return txt_u

def unwiki(txt_u):
    filter_mediawiki = mediawiki.MediawikiFilter()
    filter_html = html.HtmlFilter()
    txt_u = filter_mediawiki.get_wiki_body(txt_u)
    txt_u = filter_html.resolve_specialchars(txt_u)
    txt_u = filter_mediawiki.unmarkup(txt_u)
    txt_u = filter_html.unmarkup(txt_u)
    return txt_u


if __name__ == "__main__":
    import decoder

    import fetcher
    ret = fetcher.fetch('http://en.wikipedia.org/w/index.php?title=Linguistics&action=edit')
    txt_u = decoder.detect_decode(ret.txt_byte)
    txt_u = unwiki(txt_u) or unhtml(txt_u)
    print(decoder.encode(txt_u))
    sys.exit()

    txt_byte = open(sys.argv[1]).read()
    txt_u = decoder.detect_decode(txt_byte)
    txt_u = unwiki(txt_u) or unhtml(txt_u)
    print(decoder.encode(txt_u))
    sys.exit()


#!/usr/bin/env python
# -*- coding: UTF-8 -*-

import os
import random
import re
import tempfile
import time
import urllib
import urlparse
import traceback
import sys

from lib.spiderfetch import fetch
from lib.spiderfetch import spider
from lib.spiderfetch import urlrewrite
from lib.spiderfetch import web

import decoder
import fetcher
import io
import unmarkup

def url_handler(url_u, dir='/tmp/t'):
    if not os.path.isdir(dir):
        os.makedirs(dir)

    os.environ["ORIG_FILENAMES"] = "1"
    filename = os.path.join(dir, urlrewrite.url_to_filename(url_u)) + '.txt'

    ret = fetcher.fetch(url_u)
    txt_u = decoder.detect_decode(ret.txt_byte)
    txt_u = unmarkup.unwiki(txt_u)

    # add license notice
    tm = time.strftime("%a, %d %b %Y %H:%M:%S", time.localtime())
    notice = u"\n\n%s\nRetrieved on %s from:\n  %s" % ('-'*78, tm, ret.url_u)
    notice += (u"\nLicensed under CC-BY-SA, see %s" %
               "http://creativecommons.org/licenses/by-sa/3.0/")
    txt_u += notice

    txt_byte = decoder.encode(txt_u)
    open(filename, 'w').write(txt_byte)

def pause():
    delay = random.randint(15, 60)
    io.output("Pausing for %s seconds..." % delay)
    time.sleep(delay)

def get_regex_filter(url_u):
    tup = urlparse.urlparse(url_u)
    filter_regex = u"^%s://%s%s$" % (tup.scheme, tup.netloc, u'/wiki/[^:]+')
    return filter_regex

def fetch_gracefully(url_byte, filename):
    """Simplified adaptation of spiderfetch.py:get_url()"""
    getter = fetch.Fetcher(url=url_byte, filename=filename)
    getter.write_progress = lambda *args, **kw: None # no output or logging

    while True:
        try:
            getter.launch_w_tries()
            break
        except fetch.ChangedUrlWarning, e:
            url = urlrewrite.rewrite_urls(getter.url, [e.new_url]).next()
            getter.url = url

def get_page(url_byte):
    try:
        (_, filename) = tempfile.mkstemp()
        fetch_gracefully(url_byte, filename)
        txt_byte = open(filename, 'r').read()
        return txt_byte
    finally:
        os.unlink(filename)

def find_urls_in_page(web, txt_byte, url_u, url_byte):
    urls_byte = []
    for u_b in spider.unbox_it_to_ss(spider.findall(txt_byte)):
        urls_byte.append(u_b)
    urls_byte = sorted(list(set(urls_byte)))

    filter_regex = get_regex_filter(url_u)

    candidates_byte = []
    for u_b in urlrewrite.rewrite_urls(url_byte, urls_byte):
        if re.match(filter_regex, u_b) and url_byte != u_b:
            if u_b not in web:
                web.add_url(u_b, [])
                candidates_byte.append(u_b)

    # if no candidate links are found, fall back on visited urls
    if len(candidates_byte) == 0:
        candidates_byte = web.urls()

    return candidates_byte

def pick_url(candidates_byte, encoding='utf-8'):
    pick = random.randint(0, len(candidates_byte) - 1)

    chosen_byte = candidates_byte[pick]
    chosen_byte = urllib.unquote(chosen_byte)
    chosen_u = decoder.decode(chosen_byte, encoding)

    return chosen_u

def find_next(url_u, web, handler=None):
    url_byte = decoder.encode(url_u)

    if handler:
        io.output("Running handler with page: %s" % url_byte)
        handler(url_u)

    io.output("Spidering page: %s" % url_byte)
    txt_byte = get_page(url_byte)

    candidates_byte = find_urls_in_page(web, txt_byte, url_u, url_byte)
    encoding = decoder.detect_encoding(txt_byte)
    chosen_u = pick_url(candidates_byte, encoding=encoding)

    return chosen_u


if __name__ == '__main__':
    url_byte = 'http://en.wikipedia.org/wiki/Main_Page'
    url_byte = 'http://ar.wikipedia.org/wiki/الصفحة_الرئيسية'
    url_byte = 'http://pt.wikipedia.org/wiki/Casa_da_Cascata'
    url_byte = 'http://it.wikipedia.org/wiki/Special:Random'

    web = web.Web()
    web.add_url(url_byte, [])

    url_u = decoder.decode(url_byte, 'utf-8')
    depth = -1
    while depth != 0: # easy way to set depth as infinite
        depth -= 1
        try:
            url_u = find_next(url_u, web, handler=url_handler)
        except:
            io.output("Recovering from exception:")
            io.output(traceback.format_exc())
            url_u = pick_url(web.urls())

        pause() # less hammer

# -*- coding: UTF-8 -*-

import re
import socket
import urllib
import urlparse

import decoder
import io
import unmarkup

class Retrieved(object):
    def __init__(self, txt_byte, url_u):
        self.url_u = url_u
        self.txt_byte = txt_byte

def display_url(url_u):
    url_byte = decoder.encode(url_u)
    url_byte = urllib.unquote(url_byte) # get rid of %20 etc
    return url_byte

def fetch(url_u):
    user_agent = "Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 6.0)"
    urllib.URLopener.version = user_agent
    socket.setdefaulttimeout(120)

    # are we fetching from pedia?
    wiki = False
    parse_obj = urlparse.urlparse(url_u)
    if re.match(u'.*wikipedia[.]org$', parse_obj.netloc):
        match = re.search(u'^[/]wiki[/](.*)', parse_obj.path)
        if match:
            wiki = True
            article = match.group(1)
            pageurl_u = url_u # backup pageurl
            url_u = (u'http://%s/w/index.php?title=%s&action=edit' %
                     (parse_obj.netloc, article))
        else:
            io.message("Failed to redirect url to edit page: %s" %
                       display_url(url_u))

    io.message("Fetch url: %s" % display_url(url_u))
    txt_byte = urllib.urlopen(decoder.encode(url_u)).read()

    # if wiki, detect redirect (only one)
    if wiki:
        txt_u = decoder.detect_decode(txt_byte)
        txt_u = unmarkup.get_wiki_body(txt_u)
        match = re.search('[#]REDIRECT[ ][[]{2}([^\]]+)[\]]{2}', txt_u)
        if match:
            article = match.group(1)
            article = article[0].upper() + article[1:]
            article = re.sub('[ ]', '_', article)
            # backup pageurl
            pageurl_u = (u'http://%s/wiki/%s' % (parse_obj.netloc, article))
            url_u = (u'http://%s/w/index.php?title=%s&action=edit' %
                     (parse_obj.netloc, article))

            io.message("Detected a wiki redirect to: %s" % display_url(url_u))
            txt_byte = urllib.urlopen(decoder.encode(url_u)).read()

    try:
        url_u = pageurl_u
    except UnboundLocalError:
        pass
    retrieved = Retrieved(txt_byte, url_u)

    return retrieved

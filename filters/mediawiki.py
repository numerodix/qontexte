import re

from filters import general

class MediawikiFilter(object):
    def __init__(self):
        self.filter_general = general.GeneralFilter()

    def get_wiki_body(self, txt_u):
        match = re.search(u'(?is)[<]textarea.*[>](.*?)[<][/]textarea[>]', txt_u)
        if not match:
            return txt_u
        return match.group(1)

    def un_format(self, txt_u):
        """ref: http://www.mediawiki.org/wiki/Help:Formatting"""

        # bold and italics markup
        txt_u = re.sub(u"(?im)[']{5}(?P<x>.*?)[']{5}", '\g<1>', txt_u)

        # bold markup
        txt_u = re.sub(u"(?im)[']{3}(?P<x>.*?)[']{3}", '\g<1>', txt_u)

        # italics markup
        txt_u = re.sub(u"(?im)[']{2}(?P<x>.*?)[']{2}", '\g<1>', txt_u)

        # <nowiki> markup
        txt_u = re.sub(u"(?im)[<]nowiki[>](?P<x>.*?)[<][/]nowiki[>]", '\g<1>', txt_u)


        # headline level 6 markup
        txt_u = re.sub(u"(?im)^[=]{6}(?P<x>.*?)[=]{6}", '\g<1>', txt_u)

        # headline level 5 markup
        txt_u = re.sub(u"(?im)^[=]{5}(?P<x>.*?)[=]{5}", '\g<1>', txt_u)

        # headline level 4 markup
        txt_u = re.sub(u"(?im)^[=]{4}(?P<x>.*?)[=]{4}", '\g<1>', txt_u)

        # headline level 3 markup
        txt_u = re.sub(u"(?im)^[=]{3}(?P<x>.*?)[=]{3}", '\g<1>', txt_u)

        # headline level 2 markup
        txt_u = re.sub(u"(?im)^[=]{2}(?P<x>.*?)[=]{2}", '\g<1>', txt_u)

        # headline level 1 markup
        txt_u = re.sub(u"(?im)^[=]{1}(?P<x>.*?)[=]{1}", '\g<1>', txt_u)


        # horizontal rule
        txt_u = re.sub(u"(?im)----", '\n', txt_u)

        return txt_u

    def un_link(self, txt_u):
        """ref: 
            http://www.mediawiki.org/wiki/Help:Links
            http://www.mediawiki.org/wiki/Help:Images
            Nesting rejected, will only match inner pair
        """

        # language link (will also match images and media)  [[fr:Chine]]
        txt_u = re.sub(u"(?im)[\[]{2}[:]?[-a-zA-Z0-9]+[:][^[]*?[\]]{2}", '', txt_u)

        # internal link  [[Main Page]]
        txt_u = re.sub(u"(?im)[\[]{2}(?P<x>[^|[]*?)[\]]{2}", '\g<1>', txt_u)

        # piped link  [[Main Page|different text]]
        txt_u = re.sub(u"(?im)[\[]{2}[^|[]+?[|](?P<x>[^|[]+?)[\]]{2}", '\g<1>', txt_u)

        # media link
        txt_u = re.sub(u"(?im)[\[]{2}[:]?[A-Z][a-z]+[:][^[]*?[\]]{2}", '', txt_u)

        # external link with caption
        txt_u = re.sub(u"(?im)[\[]{1}[^ []+?[ ]+(?P<x>[^[]*?)[\]]{1}", '\g<1>', txt_u)

        # external link
        txt_u = re.sub(u"(?im)[\[]{1}(?P<x>[^[]*?)[\]]{1}", '\g<1>', txt_u)

        return txt_u

    def un_misc(self, txt_u):
        """ref: http://www.mediawiki.org/wiki/Help:Tables"""
        # <ref> markup
        txt_u = re.sub(u"(?im)[<]ref.*?[>].*?[<][/]ref[>]", '', txt_u)
        txt_u = re.sub(u"(?im)[<]ref.*?[/]?[>]", '', txt_u)

        # [ ] markup - refuse nested blocks, do more passes instead
        txt_u = re.sub(u"(?im)[[][^[]*?[]]", '', txt_u)
        txt_u = re.sub(u"(?im)[[][^[]*?[]]", '', txt_u)
        txt_u = re.sub(u"(?im)[[][^[]*?[]]", '', txt_u)
        txt_u = re.sub(u"(?im)[[][^[]*?[]]", '', txt_u)

        # { } markup - refuse nested blocks, do more passes instead
        txt_u = re.sub(u"(?im)[{][^{]*?[}]", '', txt_u)
        txt_u = re.sub(u"(?im)[{][^{]*?[}]", '', txt_u)
        txt_u = re.sub(u"(?im)[{][^{]*?[}]", '', txt_u)
        txt_u = re.sub(u"(?im)[{][^{]*?[}]", '', txt_u)
        txt_u = re.sub(u"(?im)[{][^{]*?[}]", '', txt_u)
        txt_u = re.sub(u"(?im)[{][^{]*?[}]", '', txt_u)

        return txt_u

    def unmarkup(self, txt_u):
        txt_u = self.un_format(txt_u)
        txt_u = self.un_link(txt_u)
        txt_u = self.un_misc(txt_u)
        txt_u = self.filter_general.do_stylistic(txt_u)
        return txt_u

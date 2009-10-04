import re

class GeneralFilter(object):
    def un_dos_linebreaks(self, txt_u):
        # dos line endings
        txt_u = re.sub(u'(?s)\r', '', txt_u)
        return txt_u

    def un_tags(self, txt_u):
        # kill tags <tag>
        txt_u = re.sub(u'(?s)[<].*?[>]', '', txt_u)
        return txt_u

    def un_spaces(self, txt_u):
        # leading spaces
        txt_u = re.sub(u'(?m)^[ \t]*', '', txt_u)

        # trailing spaces
        txt_u = re.sub(u'(?m)[ \t]*$', '', txt_u)
        return txt_u

    def un_linebreaks(self, txt_u):
        # too many linebreaks in a row
        txt_u = re.sub(u'(?s)(\n\s*){3,}', '\n\n', txt_u)

        # leading linebreaks
        txt_u = re.sub(u'(?m)^\n*', '', txt_u, 1)

        # trailing linebreaks
        txt_u = re.sub(u'(?s)\n*$', '', txt_u)
        return txt_u

    def do_stylistic(self, txt_u):
        # empty parens left behind?
        txt_u = re.sub(u"(?im)[ ][(][)]", '', txt_u)

        # sentence stop separated from its word?
        txt_u = re.sub(u"(?im)(?P<w>\w)\s(?P<x>[.,?!])", '\g<1>\g<2>', txt_u)

        # too many spaces?
        txt_u = re.sub(u"(?im)[ ]{2,}", ' ', txt_u)

        return txt_u

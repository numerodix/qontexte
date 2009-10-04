from htmlentitydefs import name2codepoint
import re

from filters import general

class HtmlFilter(object):
    entity_re = re.compile(u'&(?:(#)(\d+)|([a-zA-Z]+));')

    def __init__(self):
        self.filter_general = general.GeneralFilter()

    def resolve_specialchars(self, txt_u):
        """ref: http://groups.google.com/group/comp.lang.python/browse_frm/thread/9b7bb3f621b4b8e4/3b00a890cf3a5e46?q=htmlentitydefs&rnum=3&hl=en&pli=1"""
        def repl_func(match):
            if match.group(1): # Numeric character reference
                return unichr(int(match.group(2)))
            else:
                return unichr(name2codepoint[match.group(3)])
        try:
            return self.entity_re.sub(repl_func, txt_u)
        except:
            print("resolve_specialchars failed")
            return txt_u

    def unmarkup(self, txt_u):
        # <script> tag
        txt_u = re.sub(u'(?is)[<]script.*?[>].*?[<][/]script[>]', '', txt_u)

        # <style> tag
        txt_u = re.sub(u'(?is)[<]style.*?[>].*?[<][/]style[>]', '', txt_u)

        # <!-- comments -->
        txt_u = re.sub(u'(?s)[<][!][-][-].*?[-][-][>]', '', txt_u)


        # preserve linebreaks <br>
        txt_u = re.sub('(?is)[<]br[>]', '\n', txt_u)

        # resolve special characters
        txt_u = self.resolve_specialchars(txt_u)

        # kill tags <tag>
        txt_u = self.filter_general.un_tags(txt_u)


        # leading spaces and trailing spaces
        txt_u = self.filter_general.un_spaces(txt_u)


        # kill extra linebreaks
        txt_u = self.filter_general.un_linebreaks(txt_u)
        
        # dos line endings
        txt_u = self.filter_general.un_dos_linebreaks(txt_u)

        return txt_u


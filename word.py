# -*- coding: UTF-8 -*-

import codecs
import re

import decoder
import unmarkup

class Hit(object):
    def __init__(self, line, pos):
        self._line = line
        self._pos = pos

    def get_line(self):
        return self._line

    def get_pos(self):
        return self._pos

class Word(object):
    def __init__(self, _word):
        self._word = _word
        self._hits = []

    def get(self):
        return self._word

    def get_len(self):
        return len(self._word)

    def get_hits(self):
        return self._hits

    def add_hit(self, line, pos):
        self._hits.append(Hit(line, pos))

    def len_hits(self):
        return len(self._hits)

class Text(object):
    # punctuation surrounding a word
    single_quotes_s = u'\'`’'
    quotes_s = u'„"”“«»'
    puncs_s = u'.,…:;?!'
    dashes_s = u'\-–—'
    symbols_s = u'°¹²³ªº'
    others_s = u'_<>()[\]{}'
    punctuation_s = (single_quotes_s + quotes_s + puncs_s + dashes_s +
                     symbols_s + others_s)
    punctuation = re.compile(u'[%s]' % punctuation_s)

    # invalid character sequence
    invalid_s = u'0-9=|\\/+*&^%$#@~'
    invalid = re.compile(u'^[%s%s]*$' % (invalid_s, punctuation_s))

    delimiter = re.compile(u'[ \t\n\r\f\v%s%s.,]' % (single_quotes_s,
                                                     dashes_s))
    linebreak = re.compile(u'\n')

    def __init__(self):
        self.txt_u = None
        self.index = None
        self.positions = None
        self.lines = None

    def get_txt_u(self):
        return self.txt_u

    def get_word_obj(self, word_s):
        return self.index[word_s]

    def set_from_txt_u(self, txt_u):
        self.txt_u = txt_u

    def set_from_txt_byte(self, txt_byte, encoding, untag=False):
        txt_u = decoder.decode(txt_byte, encoding)
        if untag:
            txt_u = unmarkup.unhtml(txt_u)
        self.txt_u = txt_u

    def set_from_file(self, filename):
        encoding = decoder.detect_encoding(filename=filename)
        txt_u = codecs.open(filename, 'rU', encoding).read()
        self.txt_u = txt_u

    def do_index(self, delim=None, linebreak=None, invalid=None, punctuation=None):
        if not delim: delim=self.delimiter
        if not linebreak: linebreak=self.linebreak
        if not invalid: invalid=self.invalid

        if self.txt_u == None:
            raise Exception("No text set")

        index = {}
        positions = []

        cursor = -1
        line = 0
        word_s = ''
        for char in self.txt_u:
            # positional bookkeeping
            cursor += 1
            if linebreak.match(char):
                line += 1

            # non delim character, append to current word
            if not delim.match(char):
                word_s += char

            # the end of a word, index the current word
            else:
                word_line = line + 1
                word_pos = cursor - len(word_s)
                word_s, word_pos =\
                        self.__class__.cleanup_word(word_s, word_pos,
                                                    punctuation=punctuation)

                # skip empties or invalid chars
                if not invalid.match(word_s):

                    # index word
                    if word_s not in index:
                        word_obj = Word(word_s)
                        index[word_s] = word_obj
                    index[word_s].add_hit(word_line, word_pos)
                    positions.append( (word_pos, index[word_s]) )

                # reset current word
                word_s = ''

        self.index = index
        self.positions = positions
        self.lines = line

    def by_freq(self, desc=True):
        if self.index == None:
            raise Exception("I have no index")

        # hash by freq
        idx = {}
        for word_obj in self.index.values():
            freq = word_obj.len_hits()
            if freq not in idx:
                idx[freq] = []
            idx[freq].append(word_obj)

        # sort by freq, yield elems
        for freq in sorted(idx.keys(), reverse=desc):
            words_obj = sorted(idx[freq],
                               cmp=lambda x,y: cmp(x.get().lower(),
                                                   y.get().lower()))
            for word_obj in words_obj:
                yield word_obj, freq

    # should be a binary search tree, not sequential
    def find_word_near_pos(self, pos):
        word_obj = None
        for (i, (next_p, next_obj)) in enumerate(self.positions):
            if pos <= next_p:
                # selection start at word start
                if pos == next_p:
                    word_obj = next_obj
                    pos = next_p
                    break
                (prev_p, prev_obj) = self.positions[i-1]
                # selection inside a word
                if pos < prev_p + prev_obj.get_len():
                    word_obj = prev_obj
                    pos = prev_p
                    break
                # are we closer to the previous word
                if (pos - (prev_p+prev_obj.get_len())) < (next_p - pos):
                    word_obj = prev_obj
                    pos = prev_p
                    break
                # or the next?
                else:
                    word_obj = next_obj
                    pos = next_p
                    break
        return pos, word_obj

    def get_fragments(self, word_s):
        length = 30
        word_obj = self.index[word_s]
        for hit in word_obj.get_hits():
            line = hit.get_line()
            pos = hit.get_pos()

            lower = max(0, pos - length)
            upper = min(len(self.txt_u), pos + length)

            prefix = self.txt_u[lower:pos]
            suffix = self.txt_u[pos+len(word_s):upper]

            # linebreaks into spaces, contract long spaces
            prefix = re.sub('\n', ' ', prefix)
            suffix = re.sub('\n', ' ', suffix)
            prefix = re.sub('\s{2,}', ' ', prefix)
            suffix = re.sub('\s{2,}', ' ', suffix)

            # kill space before and after, but not punctuation
            if prefix and prefix[-1] == ' ':
                prefix = ' ' + prefix[:-1]
            if suffix and suffix[0] == ' ':
                suffix = suffix[1:] + ' '
    
            # pad fragment if too short
            if len(prefix) < length:
                prefix = ' '*(length - len(prefix)) + prefix
            if len(suffix) < length:
                suffix = suffix + ' '*(length - len(suffix))

            yield line, pos, prefix, word_s, suffix

    @classmethod
    def cleanup_word(cls, word_s, pos, punctuation=None):
        if not punctuation: punctuation = cls.punctuation

        while word_s and punctuation.match(word_s[-1]):
            word_s = word_s[:-1]
        while word_s and punctuation.match(word_s[0]):
            word_s = word_s[1:]
            pos += 1
        return word_s, pos



if __name__ == "__main__": 
    def print_by_freq(data):
        for (w,f) in data:
            print f, w.get().encode('utf-8'),
            for h in w.get_hits():
                print h.get_pos(),
            print

    import sys
    text = Text()
    text.set_from_file(sys.argv[1])
    text.do_index()
    data = text.by_freq()
    print_by_freq(data)

    import fetcher
    url_u = u'http://www.dagbladet.no'
    text = Text()
    ret = fetcher.fetch(url_u)
    encoding = decoder.detect_encoding(ret.txt_byte)
    text.set_from_txt_byte(ret.txt_byte, encoding, untag=True)
    text.do_index()
    data = text.by_freq()
    print_by_freq(data)
    print(encoding)

    sys.exit()

    def out(dct, f):
        ws = dct.keys()
        ws = sorted(ws, cmp=lambda x,y: cmp(x.lower(), y.lower()))
        s = ''
        for w in ws:
            s += '%-6.6s  %s\n' % (dct[w].len_hits(), w)
        codecs.open(f, 'w', 'utf-8').write(s)
    
    (text_len, s) = text.do_index(text._text)
    print text_len
    out(s, 's')
    (_, t) = text.do_index(text._text, invalid=re.compile('^[,]$'), punctuation='')
#    t = text.do_index(text._text, invalid=re.compile('^[,]$'), punctuation=re.compile('~'))
    out(t, 't')

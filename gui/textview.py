from PyQt4 import QtCore
from PyQt4 import QtGui

import encoding
import exceptions

class TextView(QtGui.QGroupBox):
    def __init__(self, parent=None):
        super(TextView, self).__init__(parent)

        self.textwidget = None

        self.text = None
        self.encoding = None
        self.path = None

        self.widget_init()

    def widget_init(self):
        # set title
        self.setTitle("Document")

        self.encodingselect = EncodingSelect()

        # create text viewport
        self.textwidget = QtGui.QTextEdit(self)

        # set layout
        box = QtGui.QVBoxLayout()
        box.addWidget(self.encodingselect)
        box.addWidget(self.textwidget)
        self.setLayout(box)
        
        # save original textcharformat object
        self.textcharformat_orig = self.textwidget.textCursor().charFormat()

        # widget settings
        self.textwidget.setReadOnly(True)

        # superhighlighted word is unique
        self.superhighlighted = None

        # highlight colors
        self.color_highlight = (161, 255, 211)
        self.color_superhighlight = (247, 181, 148)

    def get_textview_widget(self):
        return self.textwidget

    def get_encodingcombo_widget(self):
        return self.encodingselect.get_encodingcombo_widget()

    def set_text(self, text, encoding, path):
        self.text = text
        self.encoding = encoding
        self.path = path
        self.textwidget.setPlainText(self.text.get_txt_u())
        self.encodingselect.set_encoding(encoding)

    def get_file_path(self):
        return self.path

    def clear_formatting(self):
        # reset all formatting
        cursor = self.textwidget.textCursor()
        cursor.movePosition(QtGui.QTextCursor.Start)
        cursor.movePosition(QtGui.QTextCursor.End, QtGui.QTextCursor.KeepAnchor)
        cursor.setCharFormat(self.textcharformat_orig)
        # wipe superhighlight slot
        self.superhighlighted = None

    def highlight(self, pos, length, super=False):
        cursor = self.textwidget.textCursor()

        cursor.setPosition(pos, QtGui.QTextCursor.MoveAnchor)
        cursor.setPosition(pos+length, QtGui.QTextCursor.KeepAnchor)

        format = QtGui.QTextCharFormat()
        font = format.font()
        font.setBold(True)
        format.setFont(font)
        color = QtGui.QColor(*self.color_highlight)
        if super:
            color = QtGui.QColor(*self.color_superhighlight)
        brush = QtGui.QBrush(color)
        format.setBackground(brush)

        cursor.setCharFormat(format)

    def superhighlight(self, pos, length):
        if self.superhighlighted:
            (p, l) = self.superhighlighted
            self.highlight(p, l)
        self.highlight(pos, length, super=True)
        self.superhighlighted = (pos, length)

    def scroll_to(self, pos):
        cursor = self.textwidget.textCursor()
        cursor.setPosition(pos, cursor.MoveAnchor)
        self.textwidget.setTextCursor(cursor)

    def get_selected_word(self):
        cursor = self.textwidget.textCursor()
        pos = cursor.selectionStart()
        return self.text.find_word_near_pos(pos)

    def get_selected_encoding(self):
        return self.encodingselect.get_selected_encoding()

class EncodingSelect(QtGui.QWidget):
    def __init__(self, parent=None):
        super(EncodingSelect, self).__init__(parent)
        
        self.bylang = {}
        self.byenc = {}

        self.langs = []
        self.encs = []

        self.lock = None

        self.widget_init()

    def widget_init(self):
        # gui
        self.countrycombo = QtGui.QComboBox()
        self.encodingcombo = QtGui.QComboBox()

        box = QtGui.QHBoxLayout()
        box.addWidget(self.countrycombo)
        box.addWidget(self.encodingcombo)
        self.setLayout(box)

        # events
        self.connect(self.countrycombo,
                     QtCore.SIGNAL("currentIndexChanged(int)"),
                     self.handle_language_changed)

        # populate
        self.bylang, self.byenc = encoding.generate_encoding_table()
        self.langs = self.bylang.keys()
        self.langs = sorted(self.langs, cmp=lambda x,y: cmp(x.lower(), y.lower()))

        self.countrycombo.insertItems(0, self.langs)

    def get_encodingcombo_widget(self):
        return self.encodingcombo

    def set_encoding(self, encoding):
        # find what language is selected
        index = self.countrycombo.currentIndex()
        lang = self.langs[index]

        # if this encoding doesn't apply to the current language, find a
        # language that matches
        if lang not in self.byenc[encoding]:
            langid = self.langs.index(lang)
            self.countrycombo.setCurrentIndex(langid)

        encid = self.encs.index(encoding)
        self.encodingcombo.setCurrentIndex(encid)

    def get_selected_encoding(self):
        if self.lock:
            raise exceptions.EventCollisionError()
        index = self.encodingcombo.currentIndex()
        return self.encs[index]

    def handle_language_changed(self):
        index = self.countrycombo.currentIndex()
        lang = self.langs[index]

        self.encs = self.bylang[lang]
        self.encs = sorted(self.encs, cmp=lambda x,y: cmp(x.lower(), y.lower()))

        # set lock so that the signal on changed selection index for encoding
        # combo gets dropped
        self.lock = True
        self.encodingcombo.clear()
        self.encodingcombo.insertItems(0, self.encs)
        self.lock = False

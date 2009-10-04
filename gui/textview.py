from PyQt4 import QtCore
from PyQt4 import QtGui

class TextView(QtGui.QGroupBox):
    def __init__(self, parent=None):
        super(TextView, self).__init__(parent)

        self.textwidget = None
        self.text = None

        self.widget_init()

    def widget_init(self):
        # set title
        self.setTitle("Document")

        # create table
        self.textwidget = QtGui.QTextEdit(self)

        # set layout
        box = QtGui.QVBoxLayout()
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

    def get_active_widget(self):
        return self.textwidget

    def set_text(self, text):
        self.text = text
        self.textwidget.setPlainText(self.text.get_txt_u())

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

from PyQt4 import QtCore
from PyQt4 import QtGui

class UrlInput(QtGui.QWidget):
    def __init__(self, parent=None):
        super(UrlInput, self).__init__(parent)

        self.widget_init()

    def widget_init(self):
        self.label = QtGui.QLabel("Document:")
        self.url_input = UrlLineEdit(self)

        # set layout
        box = QtGui.QHBoxLayout()
        box.addWidget(self.label)
        box.addWidget(self.url_input)
        self.setLayout(box)

    def get_active_widget(self):
        return self.url_input

    # adapt QLineEdit interface

    def setText(self, txt):
        self.url_input.setText(txt)

    def text(self):
        return self.url_input.text()

class UrlLineEdit(QtGui.QLineEdit):
    """A modified QLineEdit that displays a javascript style input hint when
    focus is lost and input is null"""
    def __init__(self, parent=None):
        super(UrlLineEdit, self).__init__(parent)

        self.style_plain = "QLineEdit {}"
        self.style_hint = "QLineEdit { color: gray; font: italic; }"

        self.setStyleSheet(self.style_plain)
        self.hint = None

    def setText(self, *args):
        self.__class__.__base__.setText(self, *args)
        if len(args) > 0 and args[0]:
            self.setStyleSheet(self.style_plain)
            self.hint = False

    def focusInEvent(self, *args):
        self.__class__.__base__.focusInEvent(self, *args)
        if self.hint:
            self.setStyleSheet(self.style_plain)
            self.__class__.__base__.setText(self, "")
            self.hint = False

    def focusOutEvent(self, *args):
        self.__class__.__base__.focusOutEvent(self, *args)
        txt = unicode(self.text())
        if not txt and not self.hint:
            self.setStyleSheet(self.style_hint)
            self.__class__.__base__.setText(self,
                                            "Enter http url or file path and hit Return")
            self.hint = True

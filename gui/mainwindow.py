import os
import sys

from PyQt4 import QtCore
from PyQt4 import QtGui

import gui.textview
import gui.urlinput
import gui.wordhitview
import gui.wordlistview

import model.wordlistmodel

import decoder
import fetcher
import unmarkup
import word

class MainWindow(QtGui.QMainWindow):
    def __init__(self, app):
        super(MainWindow, self).__init__()
        self.app = app

        self.init_gui()

    def create_action(self, text, slot=None, shortcut=None, icon=None,
                      tip=None, checkable=False, signal="triggered()"):
        action = QtGui.QAction(text, self)
        if icon is not None:
            action.setIcon(QtGui.QIcon(":/%s.png" % icon))
        if shortcut is not None:
            action.setShortcut(shortcut)
        if tip is not None:
            action.setToolTip(tip)
            action.setStatusTip(tip)
        if slot is not None:
            self.connect(action, QtCore.SIGNAL(signal), slot)
        if checkable:
            action.setCheckable(True)
        return action

    def add_actions(self, target, actions):
        for action in actions:
            if action is None:
                target.addSeparator()
            else:
                target.addAction(action)

    def init_gui(self):
        self.setWindowTitle("Qontexte")

        action_close = self.create_action("Quit", slot=self.close, shortcut='Ctrl+Q')
        action_openlocal = self.create_action("Open file", slot=self.openLocal, shortcut='Ctrl+O')

        toolbar = self.addToolBar("Main")
        toolbar.setMovable(False)
        self.add_actions(toolbar, [action_close, action_openlocal, None])

        self.input_url = gui.urlinput.UrlInput()
        toolbar.addWidget(self.input_url)

        self.connect(self.input_url.get_active_widget(),
                     QtCore.SIGNAL('returnPressed()'), self.open_url)
        
        self.statusbar = self.statusBar()

        # init widgets
        self.textview = gui.textview.TextView()
        self.wordlistview = gui.wordlistview.WordListView()

        self.wordhitview = gui.wordhitview.WordHitView()

        # events
        # item selection in word list
        self.connect(self.wordlistview.get_active_widget(),
                     QtCore.SIGNAL("activated(QModelIndex)"),
                     self.wordlist_item_selected)
        # item selection in wordhit list
        self.connect(self.wordhitview.get_active_widget(),
                     QtCore.SIGNAL("activated(QModelIndex)"),
                     self.wordhit_item_selected)
        # selection changed in textview
        self.connect(self.textview.get_active_widget(),
                     QtCore.SIGNAL("copyAvailable(bool)"),
                     self.selection_changed_in_textview)

        # left side splitter
        splitter_left = QtGui.QSplitter(QtCore.Qt.Vertical)
        splitter_left.addWidget(self.textview)
        splitter_left.addWidget(self.wordhitview)

        splitter_left.setStretchFactor(0,2)
        splitter_left.setStretchFactor(1,1)

        # main splitter
        splitter = QtGui.QSplitter(QtCore.Qt.Horizontal)

        splitter.addWidget(splitter_left)
        splitter.addWidget(self.wordlistview)

        splitter.setStretchFactor(0,3)
        splitter.setStretchFactor(1,1)

        # glue to window
        self.setCentralWidget(splitter)

    def update_status(self, msg, run=None):
        self.statusbar.showMessage(msg)
        self.app.processEvents()
        if run:
            if hasattr(run, '__call__'):
                run.__call__()
            else:
                callable = run[0]
                args = run[1:]
                callable.__call__(*args)
            self.statusbar.showMessage("Idle")
            self.app.processEvents()

    def openLocal(self):
        dialog = QtGui.QFileDialog()
        path_cur = os.path.dirname(unicode(self.input_url.text()))
        dialog.setFileMode(QtGui.QFileDialog.AnyFile)
        filename = unicode(dialog.getOpenFileName(self, "Open document", path_cur))
        if filename:
            self.input_url.setText(filename)
            self.open_file(filename)

    def open_file(self, filename):
        self.update_status("Loading %s..." % filename, run=[self._load_text, filename])
        self.update_status("Indexing document...", run=self._index_text)
        self.update_status("Building word index...", run=self._render_wordlist)

    def open_url(self, url_u=None):
        if not url_u:
            url_u = unicode(self.input_url.text())
        self.update_status("Loading %s..." % url_u, run=[self._load_url, url_u])
        self.update_status("Indexing document...", run=self._index_text)
        self.update_status("Building word index...", run=self._render_wordlist)

    def _load_text(self, filename):
        # word hit list obsolete
        self.wordhitview.clear_words()
        # set text in textview
        self.text = word.Text()
        self.text.set_from_file(filename)
        self.textview.set_text(self.text)

    def _load_url(self, url_u):
        # word hit list obsolete
        self.wordhitview.clear_words()
        # set text in textview
        ret = fetcher.fetch(url_u)
        txt_u = decoder.detect_decode(ret.txt_byte)
        txt_u = unmarkup.unwiki(txt_u) or unmarkup.unhtml(txt_u)
        self.text = word.Text()
        self.text.set_from_txt_u(txt_u)
        self.textview.set_text(self.text)

    def _index_text(self):
        # index text
        self.text.do_index()

    def _render_wordlist(self):
        # assign model to table
        self.wordlistmodel = model.wordlistmodel.WordListModel(self.text, parent=self)
        self.wordlistview.set_model(self.wordlistmodel)

    def wordlist_item_selected(self, *args):
        # find row number in table
        rows = self.wordlistview.get_row_selection()
        if not rows:
            self.textview.clear_formatting()
            self.wordhitview.clear_words()
            return

        row = rows[0]

        # get me the word object from the word string
        word_obj = self.wordlistmodel.find_at_index(row)
        word_s = word_obj.get()

        self.textview.clear_formatting()

        # highlight all words occurrences in text
        for hit_obj in word_obj.get_hits():
            pos = hit_obj.get_pos()
            self.textview.highlight(pos, word_obj.get_len())

        fragments = []
        for (line, pos, prefix, word_s, suffix) in self.text.get_fragments(word_s):
            fragment = "%s*%s*%s" % (prefix, word_s, suffix)
            fragments.append( (prefix, word_s, suffix, line, pos) )
        self.wordhitview.set_words(fragments, self.wordhit_item_selected)

    def wordhit_item_selected(self, *args):
        (word_s, word_pos) = self.wordhitview.get_selected_word()
        if not word_pos:
            return

        # superhighlight word
        self.textview.superhighlight(word_pos, len(word_s))

        # scroll to word
        self.textview.scroll_to(word_pos)
    
    def selection_changed_in_textview(self, *args):
        (selection, ) = args
        if not selection:
            return

        (pos, word_obj) = self.textview.get_selected_word()
        if word_obj:
            self.wordlistview.select_word(word_obj.get())
            self.wordlist_item_selected()
            for (row, hit) in enumerate(word_obj.get_hits()):
                if hit.get_pos() == pos:
                    self.wordhitview.select_row(row)
                    self.wordhit_item_selected()
                    break

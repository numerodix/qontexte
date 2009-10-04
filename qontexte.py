#!/usr/bin/env python
#
# <desc> Vocabulary learning tool </desc>

import re
import sys

from PyQt4 import QtGui

import gui.mainwindow

class Application(QtGui.QApplication):
    def __init__(self, *args, **kw):
        super(Application, self).__init__(*args)
        
        self.init_gui()
        self.launch()

    def init_gui(self):
        self.mainwindow = gui.mainwindow.MainWindow(self)
        self.mainwindow.resize(800, 660)

    def launch(self):
        self.mainwindow.show()

        args = list(self.arguments())[1:]
        if args:
            arg = unicode(args[0])
            self.mainwindow.openPath(arg)


if __name__ == "__main__": 
    app = Application(sys.argv)
    sys.exit(app.exec_())

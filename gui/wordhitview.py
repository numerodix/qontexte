from PyQt4 import QtCore
from PyQt4 import QtGui

class WordHitView(QtGui.QGroupBox):
    def __init__(self, parent=None):
        super(WordHitView, self).__init__(parent)

        self.tablewidget = None
        self.wordhits = []

        self.widget_init()

    def widget_init(self):
        # set title
        self.setTitle("Word hits")

        # create table
        self.tablewidget = QtGui.QTableWidget(self)

        # set layout
        box = QtGui.QVBoxLayout()
        box.addWidget(self.tablewidget)
        self.setLayout(box)
        
        # hide grid
        self.tablewidget.setShowGrid(False)

        # set the font
        font = self.tablewidget.font()
        font.setFamily("Monospace")
        self.tablewidget.setFont(font)

        # set selection color
        style = "QTableView { selection-background-color: #eb5d18 }"
        self.tablewidget.setStyleSheet(style)

        # selection by row
        self.tablewidget.setSelectionBehavior(QtGui.QAbstractItemView.SelectRows)

        # hide vertical header
        verticalheader = self.tablewidget.verticalHeader()
        verticalheader.setVisible(False)

    def get_active_widget(self):
        return self.tablewidget

    def set_display_settings(self): 
        # set horizontal header properties
        horizontalheader = self.tablewidget.horizontalHeader()
        self.tablewidget.setHorizontalHeaderLabels(["prefix", "", "suffix", "line"])

        # set column width to fit contents
        self.tablewidget.resizeColumnsToContents()
        horizontalheader.setStretchLastSection(True)
#        self.tablewidget.resizeRowsToContents()

        rows_len = self.tablewidget.rowCount()
        font_size = self.tablewidget.fontMetrics().height() + 2
        for row in xrange(rows_len):
            self.tablewidget.setRowHeight(row, font_size)

    def clear_words(self):
        self.tablewidget.clear()
        self.set_display_settings()

    def set_words(self, items, callback):
        self.wordhits = items

        # import to set before adding widgets
        self.tablewidget.setRowCount(len(items))
        self.tablewidget.setColumnCount(4)

        self.tablewidget.clear()
        for (idx, (prefix, word, suffix, line, pos)) in enumerate(items):
            item_prefix = QtGui.QTableWidgetItem(prefix)
            item_word = QtGui.QTableWidgetItem(word)
            item_suffix = QtGui.QTableWidgetItem(suffix)
            item_line = QtGui.QTableWidgetItem(str(line))

            font = item_word.font()
            font.setBold(True)
            item_word.setFont(font)

            # don't allow editing
            for item in (item_prefix, item_word, item_suffix, item_line):
                flags = item.flags()
                item.setFlags(flags & ~QtCore.Qt.ItemIsEditable)

            self.tablewidget.setItem(idx, 0, item_prefix)
            self.tablewidget.setItem(idx, 1, item_word)
            self.tablewidget.setItem(idx, 2, item_suffix)
            self.tablewidget.setItem(idx, 3, item_line)

        self.set_display_settings()

    def get_selected_word(self):
        rows = list(set([cell.row() for cell in self.tablewidget.selectedIndexes()]))
        if not rows:
            return None, None
        (prefix, word, suffix, line, pos) = self.wordhits[rows[0]]
        return word, pos

    def select_row(self, row):
        self.tablewidget.selectRow(row)

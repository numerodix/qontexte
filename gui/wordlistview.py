from PyQt4 import QtCore
from PyQt4 import QtGui

class WordListView(QtGui.QGroupBox):
    def __init__(self, parent=None):
        super(WordListView, self).__init__(parent)

        self.tablewidget = None
        self.model = None

        self.widget_init()

    def widget_init(self):
        # set title
        self.setTitle("Word index")

        # create table
        self.tablewidget = QtGui.QTableView(self)

        # set layout
        box = QtGui.QVBoxLayout()
        box.addWidget(self.tablewidget)
        self.setLayout(box)

        # hide grid
        self.tablewidget.setShowGrid(False)
        
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
        horizontalheader.setStretchLastSection(True)

        # set column width to fit contents
#        self.tablewidget.resizeColumnsToContents()
#        self.tablewidget.resizeRowsToContents()

        rows_len = self.model.rowCount(self)
        font_size = self.tablewidget.fontMetrics().height() + 2
        for row in xrange(rows_len):
            self.tablewidget.setRowHeight(row, font_size)

        # enable sorting
        self.tablewidget.setSortingEnabled(True)
        self.tablewidget.sortByColumn(1, QtCore.Qt.DescendingOrder)

    def set_model(self, model):
        self.model = model
        self.tablewidget.setModel(self.model)
        self.set_display_settings()

    def get_row_selection(self):
        return [cell.row() for cell in self.tablewidget.selectedIndexes()]

    def select_word(self, word_s):
        idx = self.model.find_index_for(word_s)
        self.tablewidget.selectRow(idx)

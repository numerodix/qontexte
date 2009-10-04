import sys

from PyQt4 import QtCore

import operator
import word

class WordListModel(QtCore.QAbstractTableModel):
    def __init__(self, text, parent=None, *args):
        super(WordListModel, self).__init__(parent)
        self._text = text
        self._wordlist = [(word_obj.get(), freq) for (word_obj, freq)
                          in self._text.by_freq()]
        self._headers = ["word", "hits"]

    def rowCount(self, parent):
        return len(self._wordlist)

    def columnCount(self, parent):
        return len(self._headers)

    def data(self, index, role):
        if not index.isValid(): 
            return QtCore.QVariant() 
        elif role != QtCore.Qt.DisplayRole: 
            return QtCore.QVariant() 
        return QtCore.QVariant(self._wordlist[index.row()][index.column()]) 

    def headerData(self, col, orientation, role):
        if orientation == QtCore.Qt.Horizontal and role == QtCore.Qt.DisplayRole:
            return QtCore.QVariant(self._headers[col])
        return QtCore.QVariant()

    def sort_cmp(self, x, y):
        try:
            return cmp(x.lower(), y.lower())
        except:
            return cmp(x, y)

    def sort(self, col, order):
        self.emit(QtCore.SIGNAL("layoutAboutToBeChanged()"))
        self._wordlist = sorted(self._wordlist, key=operator.itemgetter(col),
                                cmp=self.sort_cmp)
        if order == QtCore.Qt.DescendingOrder:
            self._wordlist.reverse()
        self.emit(QtCore.SIGNAL("layoutChanged()"))

    def find_at_index(self, idx):
        word_s = self._wordlist[idx][0]
        word_obj = self._text.get_word_obj(word_s)
        return word_obj

    def find_index_for(self, word_s):
        for (i, (w_s, _)) in enumerate(self._wordlist):
            if w_s == word_s:
                return i


if __name__ == "__main__": 
    import sys
    text = word.Text(sys.argv[1])
    model = WordlistModel(text)
    print model._wordlist

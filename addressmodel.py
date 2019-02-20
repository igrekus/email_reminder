import bisect

from PyQt5.QtCore import Qt, QAbstractListModel, QModelIndex, QVariant

default_addrs = [
    'Александр Дмитриевич Першин|a.pershin@pulsarnpp.ru',
    'Станислав Андреевич Мельничук|melni4uk@pulsarnpp.ru',
    'Алексей Сергеевич Будяков|budyakov@pulsarnpp.ru',
    'Петр Сергеевич Будяков|budyakov_ps@pulsarnpp.ru'
]


class AddressModel(QAbstractListModel):

    def __init__(self, parent=None):
        super().__init__(parent)
        self._file = 'contacts.txt'
        self._addrs = dict()
        self._displayData = list()
        self.initModel()

    def initModel(self):
        addrs = self.readAddrs()
        for line in addrs:
            name, addr = line.split('|')
            shortName = self.toShortName(name)
            self._displayData.append(shortName)
            self._addrs[shortName] = (name, addr)

    def readAddrs(self):
        addrs = default_addrs
        try:
            with open(self._file, mode='rt', encoding='utf-8') as f:
                addrs = list(map(str.strip, f.readlines()))
        except FileNotFoundError as ex:
            print(ex)
            with open(self._file, mode='wt', encoding='utf-8') as f:
                for line in default_addrs:
                    f.write(line + '\n')
        return addrs

    def _saveAddrs(self):
        with open(self._file, mode='wt', encoding='utf-8') as f:
            for name, addr in sorted(self._addrs.values(), key=lambda el: el[0]):
                f.write(f'{name}|{addr}\n')

    def clear(self):
        self.beginRemoveRows(QModelIndex(), 0, len(self._displayData) - 1)
        self._displayData.clear()
        self._addrs.clear()
        self.endRemoveRows()

    def addItem(self, fio, addr):
        shortName = self.toShortName(fio)
        self._addrs[shortName] = (fio, addr)
        tmplist = self._displayData.copy()
        pos = bisect.bisect_left(tmplist, shortName) + 1
        self.beginInsertRows(QModelIndex(), pos, pos)
        self._displayData.insert(pos, shortName)
        self.endInsertRows()

        self._saveAddrs()

    def removeItem(self, row):
        self.beginRemoveRows(QModelIndex(), row, row)
        item = self._displayData[row]
        self._displayData.remove(item)
        del self._addrs[item]
        self.endRemoveRows()

        self._saveAddrs()

    def isEmpty(self):
        return not bool(self._displayData)

    def headerData(self, section, orientation, role=None):
        if role == Qt.DisplayRole or role == Qt.ToolTipRole:
            return QVariant('Имя')
        return QVariant()

    def rowCount(self, parent):
        if parent.isValid():
            return 0
        return len(self._displayData)

    def data(self, index, role=None):
        if not index.isValid():
            return QVariant

        row = index.row()

        if role == Qt.DisplayRole or role == Qt.ToolTipRole:
            if index.column() == 0:
                name, addr = self._addrs[self._displayData[row]]
                return QVariant(f'{name} <{addr}>')

        return QVariant()

    def getAddresses(self):
        return self._addrs

    def toShortName(self, name):
        last, first, mid = name.split()
        return f'{last} {first[0]}.{mid[0]}.'

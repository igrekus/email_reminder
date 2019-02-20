# -*- coding: UTF-8 -*-

from PyQt5.QtCore import Qt, QModelIndex, QVariant, QAbstractTableModel

from domainmodel import DomainModel
from mytools import const


class DeveloperModel(QAbstractTableModel):

    RoleNodeId = const.RoleNodeId

    def __init__(self, parent=None, domainModel=None):
        super().__init__(parent)
        self._domainModel: DomainModel = domainModel
        self._headers = ['id', 'ФИО', 'Email']

        self._devList = list()

    def initModel(self, data):
        self.beginResetModel()
        self._devList = data
        self.endResetModel()

    def headerData(self, section, orientation, role=None):
        if orientation == Qt.Horizontal and role == Qt.DisplayRole and section < len(self._headers):
            return QVariant(self._headers[section])
        return QVariant()

    def rowCount(self, parent=QModelIndex(), *args, **kwargs):
        if not parent.isValid():
            return len(self._devList)
        return 0

    def columnCount(self, parent=QModelIndex(), *args, **kwargs):
        return len(self._headers)

    # def setData(self, index, value, role):
    #     return True

    def data(self, index: QModelIndex, role=None):

        if not index.isValid():
            return QVariant()

        row = index.row()
        col = index.column()

        if role == Qt.DisplayRole or role == Qt.ToolTipRole:
            return QVariant(self._devList[row][col])

        elif role == Qt.CheckStateRole:
            return QVariant()

        elif role == self.RoleNodeId:
            return QVariant(self._devList[row][0])

        return QVariant()

    def flags(self, index: QModelIndex):
        f = super().flags(index)
        return f

    # def addRow(self, newId: int):
    #     self.beginInsertRows(QModelIndex(), self.rootNode.childCount(), self.rootNode.childCount())
    #     self.rootNode.appendChild(TreeNode(newId, self.rootNode))
    #     self.endInsertRows()
    #
    # @pyqtSlot(int)
    # def onContractAdded(self, conId: int):
    #     # TODO: if performance issues -- don't rebuild the whole tree, just add inserted item
    #     print("contract added:", conId)
    #     self.addRow(conId)
    #     # self.initModel()
    #
    # @pyqtSlot(int)
    # def onContractUpdated(self, conId: int):
    #     print("contract updated:", conId)
    #     del self.cache[conId]
    #
    # @pyqtSlot(int)
    # def onContractRemoved(self, conId: int):
    #     print("contract removed:", conId, "row:")
    #     del self.cache[conId]
    #     row = self.rootNode.findChild(conId)
    #     self.beginRemoveRows(QModelIndex(), row, row)
    #     self.rootNode.childNodes.pop(row)
    #     self.endRemoveRows()
    #
    # # @property
    # # def treeType(self):
    # #     return self._treeType
    # #
    # # @treeType.setter
    # # def treeType(self, treetype: int):
    # #     self._treeType = treetype
    # #     self.initModel()
    #
    # # @pyqtSlot(int, int)
    # # def itemsInserted(self, first: int, last: int):
    # #     self.beginInsertRows(QModelIndex(), first, last)
    # #     # print("table model slot:", first, last)
    # #     self.endInsertRows()
    # #
    # # @pyqtSlot(int, int)
    # # def itemsRemoved(self, first: int, last: int):
    # #     self.beginRemoveRows(QModelIndex(), first, last)
    # #     # print("table model slot:", first, last)
    # #     self.endRemoveRows()

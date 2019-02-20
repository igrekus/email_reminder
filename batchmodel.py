# -*- coding: UTF-8 -*-

from PyQt5.QtCore import Qt, QModelIndex, QVariant, pyqtSlot, QAbstractItemModel
from PyQt5.QtGui import QBrush, QColor
from attr import attr

from domainmodel import DomainModel, TIER_BATCH, TIER_SPECS
from mytools import const


# @attr
# TODO rewrite with attrs
class TreeNode(object):
    def __init__(self, data=None, parent=None):
        self._data = data
        self._parent_node = parent
        self._child_nodes = list()

    def appendChild(self, item):
        self._child_nodes.append(item)

    def child(self, row):
        return self._child_nodes[row]

    def childCount(self):
        return len(self._child_nodes)

    def parent(self):
        return self._parent_node

    def row(self):
        if self._parent_node:
            return self._parent_node._child_nodes.index(self)
        return 0

    def hasChildNodes(self):
        return bool(self._child_nodes)

    def clear(self):
        for child in self._child_nodes:
            child.clear()
        self._child_nodes.clear()
        self._data = None
        self._parent_node = None

    @property
    def data(self):
        return self._data

    def __str__(self):
        return f'TreeNode(data:{self._data} parent:{id(self._parent_node)} children:{len(self._child_nodes)}'


class BatchModel(QAbstractItemModel):

    RoleNodeId = const.RoleNodeId
    RoleFilterData = const.RoleFilterData
    RoleProgress = RoleFilterData + 1
    RoleTier = RoleProgress + 1

    COLOR_POSITIVE = 0xff92D050
    COLOR_REQUIRED = 0xffFFFF00
    COLOR_NEGATIVE = 0xffFF6767

    _default_headers = ['№', 'Запуск', 'Кристаллов всего', 'Прогресс', 'Дата запуска']

    ColumnNumber, \
    ColumnName, \
    ColumnSpecsTotal, \
    ColumnSpecsProgress, \
    ColumnDate, \
    ColumnCount = range(len(_default_headers) + 1)

    def __init__(self, parent=None, domainModel=None):
        super().__init__(parent)
        self._domainModel: DomainModel = domainModel
        self._headers = self._default_headers
        self._rootNode = TreeNode(None, None)

    def init(self):
        print('init batch model')
        for file in self._domainModel._batches:
            newNode = TreeNode(file, self._rootNode)
            specs = self._domainModel._specs.get(file.name)
            if specs:
                for spec in specs:
                    newNode.appendChild(TreeNode(spec, newNode))
            self._rootNode.appendChild(newNode)

    def clear(self):
        self._rootNode.clear()

    def headerData(self, section, orientation, role=None):
        if orientation == Qt.Horizontal and role == Qt.DisplayRole and section < len(self._headers):
            return QVariant(self._headers[section])
        return QVariant()

    def rowCount(self, parent=QModelIndex(), *args, **kwargs):
        if parent.column() > 0:
            return 0
        parent_node = parent.internalPointer() if parent.isValid() else self._rootNode
        return parent_node.childCount()

    def columnCount(self, parent=QModelIndex(), *args, **kwargs):
        return self.ColumnCount

    def index(self, row, col, parent):
        if not self.hasIndex(row, col, parent):
            return QModelIndex()

        parent_node = parent.internalPointer() if parent.isValid() else self._rootNode
        child_node = parent_node.child(row)
        return self.createIndex(row, col, child_node) if child_node else QModelIndex()

    def parent(self, index: QModelIndex):
        if not index.isValid():
            return QModelIndex()
        child_node = index.internalPointer()
        if not child_node:
            return QModelIndex()
        parent_node = child_node.parent()
        if parent_node == self._rootNode:
            return QModelIndex()
        return self.createIndex(parent_node.row(), index.column(), parent_node)

    # def setData(self, index, value, role):
    #     return True

    def data(self, index: QModelIndex, role=None):
        if not index.isValid():
            return QVariant()

        row = index.row()
        col = index.column()

        item = index.internalPointer().data

        if role == Qt.DisplayRole or role == Qt.ToolTipRole:
            if col == self.ColumnNumber:
                return QVariant(row + 1)
            elif col == self.ColumnName:
                return QVariant(item.name)
            elif col == self.ColumnSpecsTotal:
                return QVariant(item.specs_total)
            elif col == self.ColumnSpecsProgress:
                if item.tier == TIER_BATCH:
                    return QVariant(f'{item.specs_received}/{item.specs_needed}')
                elif item.tier == TIER_SPECS:
                    if item.is_received:
                        return '+'
                    else:
                        return '-'
            elif col == self.ColumnDate:
                return QVariant(str(item.date))

        elif role == self.RoleProgress:
            if col == self.ColumnSpecsProgress:
                if item.tier == TIER_BATCH:
                    return item.specs_received, item.specs_needed

        elif role == Qt.BackgroundRole:
            retcol = QColor(Qt.white)
            if col == self.ColumnSpecsProgress:
                if item.tier == TIER_SPECS:
                    if item.is_received:
                        retcol = QColor(Qt.green).lighter(150)
                    else:
                        retcol = QColor(Qt.red).lighter(150)
            return QBrush(retcol)

        elif role == self.RoleNodeId:
            return item.tier

        elif role == self.RoleTier:
            return item.tier

        return QVariant()

    def hasChildren(self, parent: QModelIndex):
        if not parent.isValid():
            return self._rootNode.hasChildNodes()
        node = parent.internalPointer()
        return node.hasChildNodes()

    def flags(self, index: QModelIndex):
        f = super().flags(index)
        return f

    @pyqtSlot(str, name='onDeviceAdded')
    def rebuildBatchModel(self, _: str):
        print('on dir changed')
        self.beginResetModel()
        self.clear()
        self.init()
        self.endResetModel()


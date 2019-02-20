from PyQt5.QtCore import Qt, QVariant, QModelIndex
from PyQt5.QtCore import QAbstractItemModel

from treenode import TreeNode


class StatModel(QAbstractItemModel):

    def __init__(self, parent=None, headers=None):
        super().__init__(parent=parent)

        self._headers = headers or list()
        self._rootNode = TreeNode(data=None, parent_node=None, column_count=5)

        self.init()

    def init(self):
        for index in [1, 2, 3, 4, 5]:
            self._rootNode.append_child_node(TreeNode(data=index, parent_node=self._rootNode, column_count=5))

    def clear(self):
        self._rootNode.clear()

    def headerData(self, section, orientation, role=None) -> QVariant:
        if orientation == Qt.Horizontal and role == Qt.DisplayRole and section < len(self._headers):
            return QVariant(self._headers[section])
        return QVariant()

    def rowCount(self, parent=QModelIndex(), *args, **kwargs) -> int:
        # return 1
        parent_node = parent.internalPointer() if parent.isValid() else self._rootNode
        return parent_node.child_node_count()

    def columnCount(self, parent=QModelIndex(), *args, **kwargs) -> int:
        return len(self._headers)

    def index(self, row, col, parent) -> QModelIndex:
        if not self.hasIndex(row, col, parent):
            return QModelIndex()

        parent_item = parent.internalPointer() if parent.isValid() else self._rootNode
        child_item = parent_item.child_node(row)
        return self.createIndex(row, col, child_item) if child_item else QModelIndex()

    def parent(self, index: QModelIndex) -> QModelIndex:
        if not index.isValid():
            return QModelIndex()
        child_node = index.internalPointer()
        if not child_node:
            return QModelIndex()
        parent_item = child_node.parent()
        if parent_item == self._rootNode:
            return QModelIndex()
        return self.createIndex(parent_item.row(), index.column(), parent_item)

    def data(self, index: QModelIndex, role=None) -> QVariant:
        if not index.isValid():
            return QVariant()

        print('heyyy')
        return QVariant('test')
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

    def hasChildren(self, parent: QModelIndex) -> bool:
        if not parent.isValid():
            return self._rootNode.has_child_nodes()
        node = parent.internalPointer()
        return node.has_child_nodes()

    # def flags(self, index: QModelIndex):
    #     f = super().flags(index)
    #     return f
    #
    # @pyqtSlot(str, name='onDeviceAdded')
    # def rebuildBatchModel(self, _: str):
    #     print('on dir changed')
    #     self.beginResetModel()
    #     self.clear()
    #     self.init()
    #     self.endResetModel()
    #
    #
    #

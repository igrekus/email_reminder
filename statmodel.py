from PyQt5.QtCore import Qt, QVariant, QModelIndex
from PyQt5.QtCore import QAbstractItemModel

from treenode import TreeNode


class StatModel(QAbstractItemModel):

    def __init__(self, parent=None, headers=None):
        super().__init__(parent)
        self._headers = headers or list()
        self._rootNode = TreeNode(None, None)

    def init(self, rootNode):
        self.beginResetModel()
        self._rootNode = rootNode
        self.endResetModel()

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
        return parent_node.child_count()

    def columnCount(self, parent=QModelIndex(), *args, **kwargs):
        return len(self._headers)

    def index(self, row, col, parent):
        if not self.hasIndex(row, col, parent):
            return QModelIndex()

        parent_node = parent.internalPointer() if parent.isValid() else self._rootNode
        child_node = parent_node.child_at(row)
        return self.createIndex(row, col, child_node) if child_node else QModelIndex()

    def parent(self, index: QModelIndex):
        if not index.isValid():
            return QModelIndex()
        child_node = index.internalPointer()
        if not child_node:
            return QModelIndex()
        parent_node = child_node.parent()
        if parent_node == self._rootNode or parent_node is None:
            return QModelIndex()
        return self.createIndex(parent_node.row(), index.column(), parent_node)

    def data(self, index: QModelIndex, role=None):
        if not index.isValid():
            return QVariant()

        col = index.column()

        node = index.internalPointer()
        if role == Qt.DisplayRole or role == Qt.ToolTipRole:
            return QVariant(node[col])

        return QVariant()

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

    # def hasChildren(self, parent: QModelIndex):
    #     if not parent.isValid():
    #         return self._rootNode.hasChildNodes()
    #     node = parent.internalPointer()
    #     return node.hasChildNodes()

    def flags(self, index: QModelIndex):
        f = super().flags(index)
        return f

    # @pyqtSlot(str, name='onDeviceAdded')
    # def rebuildBatchModel(self, _: str):
    #     print('on dir changed')
    #     self.beginResetModel()
    #     self.clear()
    #     self.init()
    #     self.endResetModel()
    #

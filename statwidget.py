import os
from collections import defaultdict
from pathlib import Path

import openpyxl
from PyQt5.QtCore import pyqtSlot
from PyQt5.QtWidgets import QWidget, QPushButton, QTreeView, QHBoxLayout, QLineEdit, QVBoxLayout, QFileDialog, \
    QAbstractItemView

from batchdomain import BatchItem, SpecItem, BatchDomain
from stattreemodel import StatTreeModel
from treenode import TreeNode
from progressbardelegate import ProgressBarDelegate


class StatWidget(QWidget):

    def __init__(self, parent=None, domain=None, headers=None):
        super().__init__(parent=parent)

        self._root = None
        self._domain = domain

        self._button = QPushButton('Открыть...')
        self._edit = QLineEdit()
        self._tree = QTreeView()

        self._model = StatTreeModel(parent=self, headers=headers)

        self._layoutControl = QHBoxLayout()
        self._layoutControl.addWidget(self._button)
        self._layoutControl.addWidget(self._edit)

        self._layoutMain = QVBoxLayout()
        self._layoutMain.addLayout(self._layoutControl)
        self._layoutMain.addWidget(self._tree)

        self.setLayout(self._layoutMain)

        self._edit.setPlaceholderText('Папка...')
        self._edit.setReadOnly(True)

        self._button.clicked.connect(self._on_button_clicked)

        self._tree.setModel(self._model)
        self._tree.setItemDelegateForColumn(3, ProgressBarDelegate())
        self._tree.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self._tree.setSelectionBehavior(QAbstractItemView.SelectRows)

    def init(self):
        self._domain.workDir = os.path.normpath(os.getcwd()) + '\\xlsx'
        self._edit.setText(self._domain.workDir)
        self._model.init(self._domain._root)

    @pyqtSlot()
    def _on_button_clicked(self):
        dialog = QFileDialog(self, 'Выбрать папку...', self._domain.workDir)
        dialog.setFileMode(QFileDialog.DirectoryOnly)
        if dialog.exec() != QFileDialog.Accepted:
            return

        self._domain.workDir = dialog.selectedFiles()[0]
        self._model.init(self._domain._root)

    @property
    def hasSelection(self):
        return self._tree.selectionModel().hasSelection()

    @property
    def rows(self):
        return sorted(map(lambda index: index.row(),  # extract row numbers
                          filter(lambda index: index.data(StatTreeModel.RoleId) == 1 and index.column() == 0,   # filter top level column 0 indexes
                                 self._tree.selectionModel().selectedIndexes())))

    def getEmailData(self, rows):
        email_data = dict()
        for batch in self._root.child_nodes:
            specs_for_dev = defaultdict(list)
            for spec in batch.child_nodes:
                if not spec['received']:
                    specs_for_dev[spec['developer']].append(spec)
            email_data[batch] = specs_for_dev

        return email_data

    def resizeTable(self, width, columns):
        for index, column in enumerate(columns):
            self._tree.setColumnWidth(index, width * column)

from PyQt5.QtCore import pyqtSlot
from PyQt5.QtWidgets import QWidget, QPushButton, QTreeView, QHBoxLayout, QLineEdit, QVBoxLayout, QFileDialog

from statmodel import StatModel
from treenode import TreeNode


class StatWidget(QWidget):

    def __init__(self, parent=None, headers=None):
        super().__init__(parent=parent)

        self._workdir = '.'

        self._button = QPushButton('Открыть...')
        self._edit = QLineEdit()
        self._tree = QTreeView()

        self._model = StatModel(parent=self, headers=headers)

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

        self.init()

    def init(self):
        root = TreeNode(None, None)

        for file in [1, 2, 3]:
            newNode = TreeNode(['1', '2', '3', '4', '5'], root)
            root.append_child(newNode)

        self._model.init(rootNode=root)

        self._tree.setModel(self._model)

    @pyqtSlot()
    def _on_button_clicked(self):
        dialog = QFileDialog(self, 'Выбрать папку...', self._workdir)
        dialog.setFileMode(QFileDialog.DirectoryOnly)
        if dialog.exec() != QFileDialog.Accepted:
            return

        self._workdir = dialog.selectedFiles()[0]





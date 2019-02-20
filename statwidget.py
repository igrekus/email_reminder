from PyQt5.QtCore import pyqtSlot
from PyQt5.QtWidgets import QWidget, QLabel, QPushButton, QTreeView, QHBoxLayout, QLineEdit, QVBoxLayout, QFileDialog

from statmodel import StatModel


class StatWidget(QWidget):

    def __init__(self, parent=None, headers=None):
        super().__init__(parent=parent)

        self._workdir = '.'

        self._button = QPushButton('Открыть...')
        self._edit = QLineEdit()
        self._tree = QTreeView()

        self._model = StatModel(headers=headers)
        self._tree.setModel(self._model)

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

    @pyqtSlot()
    def _on_button_clicked(self):
        dialog = QFileDialog(self, 'Выбрать папку...', self._workdir)
        dialog.setFileMode(QFileDialog.DirectoryOnly)
        if dialog.exec() != QFileDialog.Accepted:
            return

        self._workdir = dialog.selectedFiles()[0]





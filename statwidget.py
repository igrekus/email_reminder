from PyQt5.QtCore import pyqtSlot
from PyQt5.QtWidgets import QWidget, QLabel, QPushButton, QTreeView, QHBoxLayout, QLineEdit, QVBoxLayout

from statmodel import StatModel


class StatWidget(QWidget):

    def __init__(self, parent=None, label=''):
        super().__init__(parent=parent)

        self._button = QPushButton('Открыть...')
        self._edit = QLineEdit()
        self._tree = QTreeView()

        self._model = StatModel()

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
        print('click')





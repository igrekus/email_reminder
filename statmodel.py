from PyQt5.QtCore import QAbstractItemModel


class StatModel(QAbstractItemModel):

    def __init__(self, parent=None):
        super().__init__(parent=parent)


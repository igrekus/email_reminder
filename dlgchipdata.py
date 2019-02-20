# -*- coding: UTF-8 -*-

from PyQt5 import uic
from PyQt5.QtWidgets import QDialog, QMessageBox
from PyQt5.QtCore import Qt
from developermodel import DeveloperModel


class DlgChipData(QDialog):

    def __init__(self, parent=None, domainModel=None, uifacade=None, item=None):
        super().__init__(parent)
        self.setAttribute(Qt.WA_QuitOnClose)
        self.setAttribute(Qt.WA_DeleteOnClose)

        # create instance variables
        # ui
        self._ui = uic.loadUi('dlgchipdata.ui', self)

        # init instances
        self._domainModel = domainModel
        self._uiFacade = uifacade
        self._developerModel = DeveloperModel(parent=self, domainModel=self._domainModel)

        # data members
        self._currentItem = item
        self._newItem = None

        self._initDialog()

    def _initDialog(self):
        print('init chip data dialog')
        self._developerModel.initModel(self._domainModel.getDevelopers())
        # init widgets
        self._ui.in_TableDeveloper.setModel(self._developerModel)
        self._ui.in_TableDeveloper.setSortingEnabled(True)
        self._ui.in_TableDeveloper.resizeColumnsToContents()

        # setup signals
        self._ui.btnOk.clicked.connect(self.onBtnOkClicked)
        self._ui.btnAddDeveloper.clicked.connect(self.onBtnAddDeveloperClicked)

        # set widget data
        if self._currentItem is None:
            self._resetWidgets()
        else:
            self._updateWidgets()

    def _updateWidgets(self):
        return
        # self._ui.in_EditChipName.setText(self._currentItem.name)
        # TODO select chip dev

    def _resetWidgets(self):
        self._ui.in_EditChipName.setText('')

    def _verifyInputData(self):
        if not self._ui.in_EditChipName.text():
            QMessageBox.information(self, 'Ошибка', 'Введите название кристалла.')
            return False

        if not self._ui.in_TableDeveloper.selectionModel().selectedIndexes():
            QMessageBox.information(self, 'Ошибка', 'Выберите разработчика кристалла.')
            return False

        return True

    def _collectData(self):
        chipName = self._ui.in_EditChipName.text()
        chipDev = self._ui.in_TableDeveloper.selectionModel().selectedIndexes()[0].data(DeveloperModel.RoleNodeId)
        self._newItem = (chipName, chipDev)

    def getData(self):
        return self._newItem

    def onBtnOkClicked(self):
        if not self._verifyInputData():
            return
        self._collectData()
        self.accept()

    def onBtnAddDeveloperClicked(self):
        print('add dev')
        self._uiFacade.requestDeveloperAdd(self)
        self._developerModel.initModel(self._domainModel.getDevelopers())
        self._ui.in_TableDeveloper.resizeColumnsToContents()


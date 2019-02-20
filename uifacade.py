# -*- coding: UTF-8 -*-

from PyQt5.QtCore import QObject, QModelIndex
from PyQt5.QtWidgets import QDialog, QInputDialog, QLineEdit
from formlayout.formlayout import fedit

from dlgchipdata import DlgChipData
from dlgdevicedata import DlgDeviceData


class UiFacade(QObject):

    def __init__(self, parent=None, domainModel=None, reportManager=None, emailManager=None):
        super().__init__(parent)
        self._domainModel = domainModel
        self._reportManager = reportManager
        self._emailManager = emailManager

    def initFacade(self):
        print('init ui facade')

    def requestdeviceAdd(self):
        print('ui facade add device request')
        dialog = DlgDeviceData(domainModel=self._domainModel, uifacade=self)
        if dialog.exec() != QDialog.Accepted:
            return

        newItem = dialog.getData()
        self._domainModel.addDevice(newItem)

    def requestDeviceEdit(self, index: QModelIndex):
        # TODO don't do this shit, use proper business objects
        oldItem = self._domainModel[index.row()]
        print('ui facade edit request', oldItem)

        dialog = DlgDeviceData(domainModel=self._domainModel, uifacade=self, item=oldItem)
        if dialog.exec() != QDialog.Accepted:
            return

        self._domainModel.updateDevice(oldItem)

    def requestBatchAdd(self, caller):
        print('ui facade add batch request')
        data, ok = QInputDialog.getText(caller, 'Добавить новый заупск', 'Введите название:', QLineEdit.Normal, '')
        if not ok:
            return
        self._domainModel.addBatch(data)

    def requestChipAdd(self, caller):
        print('ui facade add chip request')
        dialog = DlgChipData(parent=caller, domainModel=self._domainModel, uifacade=self)
        if dialog.exec() != QDialog.Accepted:
            return
        data = dialog.getData()
        self._domainModel.addChip(*data)

    def requestDeveloperAdd(self, caller):
        print('ui facade add developer request')
        datalist = [('ФИО:', ''),
                    ('Email:', '')]
        data = fedit(datalist, title='Данные о разработчике', comment='Введите данные о разработчике', parent=caller)
        if data is None:
            return
        self._domainModel.addDeveloper(*data)

    def requestSendEmails(self, *creds):
        print('sending emails')
        try:
            self._emailManager.setCredentials(*creds)
            self._emailManager.send(self._domainModel.getToSend())
        except Exception as ex:
            print(ex)

# -*- coding: UTF-8 -*-

import datetime
import pony.orm as pony
from PyQt5 import uic
from PyQt5.QtWidgets import QDialog, QMessageBox, QLineEdit, QComboBox, QPlainTextEdit
from PyQt5.QtCore import Qt, QDate

import models
import mytools.const


class DlgDeviceData(QDialog):

    def __init__(self, parent=None, domainModel=None, uifacade=None, item=None):
        super().__init__(parent)
        self.setAttribute(Qt.WA_QuitOnClose)
        self.setAttribute(Qt.WA_DeleteOnClose)

        # create instance variables
        # ui
        self._ui = uic.loadUi('dlgdevicedata.ui', self)

        # init instances
        self._domainModel = domainModel
        self._uiFacade = uifacade

        # data members
        self._currentItem = item
        self._newItem = None

        self._initDialog()

    def _initDialog(self):
        print('init taskdata dialog')
        # init widgets
        self._ui.in_ComboBatch.setModel(self._domainModel.comboModels['batch'])
        self._ui.in_ComboChip.setModel(self._domainModel.comboModels['chip'])

        # setup signals
        self._ui.btnOk.clicked.connect(self.onBtnOkClicked)
        self._ui.btnAddBatch.clicked.connect(self.onBtnAddBatchClicked)
        self._ui.btnAddChip.clicked.connect(self.onBtnAddChipClicked)

        # set widget data
        if self._currentItem is None:
            self._resetWidgets()
        else:
            self._updateWidgets()

    def _updateWidgets(self):
        def formatDate(date: datetime.date):
            if isinstance(date, datetime.date):
                return QDate().fromString(date.isoformat(), 'yyyy-MM-dd')
            else:
                return QDate().fromString('2000-01-01', 'yyyy-MM-dd')

        self._ui.in_EditName.setText(self._currentItem.name)
        self._ui.in_TextNote.setPlainText(self._currentItem.description)
        self._ui.in_ComboBatch.setCurrentText(self._ui.in_ComboBatch.model().getData(self._currentItem.batch.id))
        self._ui.in_ComboChip.setCurrentText(self._ui.in_ComboChip.model().getData(self._currentItem.chip.id))
        self._ui.in_DateReceived.setDate(formatDate(self._currentItem.date_receive))
        self._ui.in_ChkNeeded.setChecked(self._currentItem.is_needed)
        self._ui.in_ChkReceived.setChecked(self._currentItem.is_received)

    def _resetWidgets(self):
        now = QDate().currentDate()
        self._ui.in_EditName.setText('')
        self._ui.in_TextNote.setPlainText('')
        self._ui.in_ComboBatch.setCurrentIndex(-1)
        self._ui.in_ComboChip.setCurrentIndex(-1)
        self._ui.in_DateReceived.setDate(now)
        self._ui.in_ChkNeeded.setChecked(False)
        self._ui.in_ChkReceived.setChecked(False)

    def _verifyInputData(self):
        # TODO format error msg with buddy label text
        def verifyLineEdit(widget):
            if not widget.text():
                return 'Заполните все поля ввода.'
            return ''

        def verifyComboBox(widget):
            if widget.currentIndex() == -1:
                return 'Выберите все опции.'
            return ''

        def verifyPlainTextEdit(widget):
            if not widget.toPlainText():
                return 'Заполните все поля ввода.'
            return ''

        widget_names = [d for d in self._ui.__dir__() if d.startswith('in_')]

        for name in widget_names:
            widget = getattr(self._ui, name)
            msg = ''
            if isinstance(widget, QLineEdit):
                msg = verifyLineEdit(widget)
            elif isinstance(widget, QComboBox):
                msg = verifyComboBox(widget)
            elif isinstance(widget, QPlainTextEdit):
                msg = verifyPlainTextEdit(widget)
            if msg:
                QMessageBox.information(self, 'Ошибка', msg)
                return False

        return True

    def _collectData(self):
        date_receive = None
        is_received = self._ui.in_ChkReceived.isChecked()
        if is_received:
            date_receive = datetime.datetime.now().date()

        with pony.db_session:
            batch = models.Batch[self._ui.in_ComboBatch.currentData(mytools.const.RoleNodeId)]
            chip = models.Chip[self._ui.in_ComboChip.currentData(mytools.const.RoleNodeId)]
            if self._currentItem is not None:
                device = models.Device[self._currentItem.id]
                device.set(name=self._ui.in_EditName.text(),
                           description=self._ui.in_TextNote.toPlainText(),
                           date_receive=date_receive,
                           batch=batch,
                           chip=chip,
                           is_needed=self._ui.in_ChkNeeded.isChecked(),
                           is_received=is_received)
            else:
                device = models.Device(name=self._ui.in_EditName.text(),
                                       description=self._ui.in_TextNote.toPlainText(),
                                       date_receive=date_receive,
                                       date_create=datetime.datetime.now().date(),
                                       batch=batch,
                                       chip=chip,
                                       is_needed=self._ui.in_ChkNeeded.isChecked(),
                                       is_received=is_received)
            pony.flush()

        self._newItem = device

    def getData(self):
        return self._newItem

    def onBtnOkClicked(self):
        if not self._verifyInputData():
            print('fail')
            return
        try:
            self._collectData()
        except Exception as ex:
            print(ex)
        self.accept()

    def onBtnAddBatchClicked(self):
        self._uiFacade.requestBatchAdd(self)
        self._ui.in_ComboBatch.setModel(self._domainModel.comboModels['batch'])
        self._ui.in_ComboBatch.setCurrentIndex(len(self._ui.in_ComboBatch.model().strList) - 1)

    def onBtnAddChipClicked(self):
        self._uiFacade.requestChipAdd(self)
        self._ui.in_ComboChip.setModel(self._domainModel.comboModels['chip'])
        self._ui.in_ComboChip.setCurrentIndex(len(self._ui.in_ComboChip.model().strList) - 1)

    def done(self, code):
        super().done(code)


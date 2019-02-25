# -*- coding: UTF-8 -*-
from os.path import isfile

from PyQt5 import uic
from PyQt5.QtWidgets import QMainWindow, QMessageBox, QFileDialog, QTreeView
from PyQt5.QtCore import Qt, QSortFilterProxyModel, pyqtSlot

from addressmodel import AddressModel
from batchmodel import BatchModel
from domainmodel import DomainModel
from emailmanager import EmailManager
from emailtemplate import EmailTemplate
from formlayout.formlayout import fedit
from progressbardelegate import ProgressBarDelegate
from statwidget import StatWidget


class MainWindow(QMainWindow):

    def __init__(self, parent=None):
        super().__init__(parent)

        self.setAttribute(Qt.WA_QuitOnClose)
        self.setAttribute(Qt.WA_DeleteOnClose)

        # create instance variables
        self._ui = uic.loadUi('mainwindow.ui', self)

        self._emailTemplate = EmailTemplate()
        self._emailManager = EmailManager(template=self._emailTemplate)

        self._addressModel = AddressModel(parent=self)

        self._ui.statBatch = StatWidget(parent=self, domain=BatchDomain(), headers=['№', 'Запуск', 'Кристаллов всего', 'Прогресс', 'Дата запуска'])
        self._ui.tabWidget.addTab(self._ui.statBatch, 'Запуски')

        self._progressDelegate = ProgressBarDelegate()

    def setupUiSignals(self):
        self._ui.editFrom.textChanged.connect(self._updateCreds)
        self._ui.editLogin.textChanged.connect(self._updateCreds)
        self._ui.editPass.textChanged.connect(self._updateCreds)
        self._ui.editHost.textChanged.connect(self._updateCreds)
        self._ui.editSMTP.textChanged.connect(self._updateCreds)
        self._ui.editIMAP.textChanged.connect(self._updateCreds)

    def initUi(self):
        self.setupUiSignals()

        self._ui.listAddress.setModel(self._addressModel)
        self._ui.textTemplate.setPlainText(self._emailTemplate.template)

        settings = dict()
        if isfile('./connect.ini'):
            with open('./connect.ini', 'rt') as f:
                for line in f.readlines():
                    tag, value = line.strip().split('=')
                    settings[tag] = value

        self._ui.editFrom.setText(settings['address'])
        self._ui.editLogin.setText(settings['login'])
        self._ui.editPass.setText(settings['pass'])

    def initDomains(self):
        self._ui.statBatch.init()

    def initDialog(self):
        print('init dialog')
        self.initUi()
        self._updateCreds('')

        self.initDomains()

        self.refreshView()

    # UI utility methods
    def refreshView(self):
        self._ui.statBatch.resizeTable(self.frameGeometry().width() - 30, [0.08, 0.60, 0.12, 0.12, 0.08])

    # event handlers
    def resizeEvent(self, event):
        self.refreshView()

    # signal processing
    @pyqtSlot()
    def on_btnOpenDir_clicked(self):
        dialog = QFileDialog(self)
        dialog.setFileMode(QFileDialog.DirectoryOnly)
        if dialog.exec() != QFileDialog.Accepted:
            return
        self._domainModel.workingDir = dialog.selectedFiles()[0]

    @pyqtSlot()
    def on_btnSendEmails_clicked(self):
        print('send emails')
        if not self._ui.statBatch.hasSelection:
            QMessageBox.information(self.parent(), 'Внимание!', 'Выберите запуски для сосздания рассылки.')
            return

        rows = self._ui.statBatch.rows

        if not self._emailManager.send(self._ui.statBatch.getEmailData(rows), self._addressModel.getAddresses()):
            QMessageBox.warning(self.parent(), 'Внимание!', 'Произошла ошибка при отправке писем, подробности в логах.')

    @pyqtSlot()
    def on_btnAddAddress_clicked(self):
        markup = (
            ('ФИО', ''),
            ('Email', '')
        )
        res = fedit(markup, title='Введите данные', comment='Добавить новый адрес')
        if res:
            fio, addr = res
            if fio.count(' ') == 2:
                self._addressModel.addItem(fio, addr)

    @pyqtSlot()
    def on_btnDelAddress_clicked(self):
        if not self._ui.listAddress.selectionModel().hasSelection():
            return
        if QMessageBox.question(self.parent(), 'Внимание!', 'Вы хотите удалить выбранную запись?') != QMessageBox.Yes:
            return
        index = self._ui.listAddress.selectionModel().selectedIndexes()[0]
        self._addressModel.removeItem(index.row())

    @pyqtSlot()
    def on_textTemplate_textChanged(self):
        self._emailTemplate.save_template(self._ui.textTemplate.toPlainText())

    @pyqtSlot(str)
    def _updateCreds(self, text):
        try:
            smtp_port = int(self._ui.editSMTP.text())
            imap_port = int(self._ui.editIMAP.text())
        except ValueError as ex:
            print('error, wrong port number')
            QMessageBox.warning(self.parent(), 'Внимание!', 'Значение порта может быть только численным.')
            self._ui.editSMTP.setText('0')
            self._ui.editIMAP.setText('0')
            return

        from_addr = self._ui.editFrom.text()
        login = self._ui.editLogin.text()
        passwd = self._ui.editPass.text()
        host = self._ui.editHost.text()

        self._emailManager.setCredentials(from_addr, login, passwd, host, smtp_port, imap_port)


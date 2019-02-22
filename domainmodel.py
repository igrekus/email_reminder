# -*- coding: UTF-8 -*-

import datetime
from collections import defaultdict

import openpyxl
import os

from pathlib import Path
from PyQt5.QtCore import QObject, pyqtSignal
from attr import attrs, attrib

TIER_BATCH, \
TIER_SPECS = range(1, 3)


@attrs
class BatchItem(object):
    _rowid = attrib(default=0, type=int)
    _tier = attrib(default=TIER_BATCH)
    _name = attrib(default='', type=str)
    _specs_total = attrib(default=0, type=int)
    _specs_needed = attrib(default=0, type=int)
    _specs_received = attrib(default=0, type=int)
    _date = attrib(default=datetime.datetime.now().date().isoformat()[:7], type=str)
    @property
    def tier(self):
        return self._tier
    @property
    def name(self):
        return self._name
    @property
    def specs_needed(self):
        return self._specs_needed
    @property
    def specs_total(self):
        return self._specs_total
    @property
    def specs_received(self):
        return self._specs_received
    @property
    def specs_left(self):
        left = self._specs_total - self._specs_received
        if left < 0:
            left = 0
        return left
    @property
    def date(self):
        return self._date
    @property
    def rowid(self):
        return self._rowid


@attrs
class SpecItem(object):
    _tier = attrib(default=TIER_SPECS)
    _name = attrib(default='', type=str)
    _is_received = attrib(default=False, type=bool)
    _rowid = attrib(default=0, type=int)
    _developer = attrib(default='', type=str)
    @property
    def tier(self):
        return self._tier
    @property
    def name(self):
        return self._name
    @property
    def is_received(self):
        return self._is_received
    @property
    def specs_needed(self):
        return ''
    @property
    def specs_total(self):
        return ''
    @property
    def specs_received(self):
        return ''
    @property
    def specs_left(self):
        return ''
    @property
    def date(self):
        return ''
    @property
    def rowid(self):
        return self._rowid
    @property
    def developer(self):
        return self._developer


class DomainModel(QObject):

    workDirChanged = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)

        self._workDir = None
        self._batches = list()
        self._specs = dict()
        print('create domain model')

    def initModel(self):
        self.workingDir = os.path.normpath(os.getcwd()) + '\\xlsx'

    def _checkFileEntry(self, entry):
        return entry.is_file() and entry.path.endswith('.xlsx')

    def _excelFiles(self):
        with os.scandir(self._workDir) as entries:
            for entry in entries:
                if self._checkFileEntry(entry):
                    yield os.path.normpath(entry.path)

    def _parseExcelFile(self, file):
        wb = openpyxl.load_workbook(file)
        ws = wb.active
        specs = list()
        total_specs = 0
        needed_specs = 0
        for row in list(ws.rows)[1:]:
            if all(row):
                rowid, desc, chip, fio, is_needed, board_date, is_received = [el.value for el in row]
                total_specs += 1
                if is_needed and is_needed == '+':
                    specs.append(SpecItem(rowid=rowid, name=f'{chip} - {desc}', developer=fio, is_received=False if is_received == '-' else True))
                    needed_specs += 1
        wb.close()
        return total_specs, needed_specs, specs

    def _processDir(self):
        for index, file in enumerate(self._excelFiles()):
            batch = Path(file).resolve().stem
            date_from_batch = batch[-7:].replace('_', '-')
            total_specs, needed_specs, specs = self._parseExcelFile(file=file)
            specs_received = sum(map(lambda el: int(el.is_received), specs))
            self._specs[batch] = specs
            self._batches.append(BatchItem(rowid=index + 1, tier=TIER_BATCH, name=batch, specs_needed=needed_specs,
                                           specs_total=total_specs, specs_received=specs_received,
                                           date=date_from_batch))

    def _buildModel(self):
        self._batches.clear()
        self._specs.clear()
        self._processDir()

    def getEmailData(self, rows):
        email_data = dict()
        for batch in [self._batches[row].name for row in rows]:
            specs_for_dev = defaultdict(list)
            for spec in self._specs[batch]:
                if not spec.is_received:
                    specs_for_dev[spec.developer].append(spec)
            email_data[batch] = specs_for_dev
        return email_data

    @property
    def workingDir(self):
        return self._workDir

    @workingDir.setter
    def workingDir(self, name):
        if os.path.isdir(name):
            self._workDir = os.path.normpath(name)
            self._buildModel()
            self.workDirChanged.emit(self._workDir)


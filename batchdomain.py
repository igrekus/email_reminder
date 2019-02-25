import datetime
import os
import openpyxl

from pathlib import Path
from attr import attrs, attrib

from stattreemodel import StatTreeModel
from treenode import TreeNode


@attrs
class BatchItem(object):
    _rowid = attrib(default=0, type=int)
    _tier = attrib(default=StatTreeModel.TIER_1)
    _name = attrib(default='', type=str)
    _specs_total = attrib(default=0, type=int)
    _specs_needed = attrib(default=0, type=int)
    _specs_received = attrib(default=0, type=int)
    _date = attrib(default=datetime.datetime.now().date().isoformat()[:7], type=str)
    def __getitem__(self, item):
        if item == 0:
            return self.rowid
        elif item == 1:
            return self.name
        elif item == 2:
            return self.specs_total
        elif item == 3:
            return f'{self.specs_received}/{self.specs_needed}'
        elif item == 4:
            return str(self.date)
        elif item == 'id':
            return self.rowid
        elif item == 'tier':
            return self.tier
        elif item == 'progress':
            return self.specs_received, self.specs_needed
        elif item == 'received':
            return True
        elif item == 'developer':
            return ''
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
    _tier = attrib(default=StatTreeModel.TIER_2)
    _name = attrib(default='', type=str)
    _is_received = attrib(default=False, type=bool)
    _rowid = attrib(default=0, type=int)
    _developer = attrib(default='', type=str)
    def __getitem__(self, item):
        if item == 0:
            return self.rowid
        elif item == 1:
            return self.name
        elif item == 2:
            return self.specs_total
        elif item == 3:
            return '+' if self.is_received else '-'
        elif item == 4:
            return str(self.date)
        elif item == 'id':
            return self.rowid
        elif item == 'tier':
            return self.tier
        elif item == 'progress':
            return 1, 1
        elif item == 'received':
            return self.is_received
        elif item == 'developer':
            return self.developer
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


class BatchDomain:

    def __init__(self):
        self._workDir = ''
        self._root = TreeNode(None, None)

    def init(self):
        print(f'init batch domain for dir {self._workDir}')
        self._buildModel()

    def _buildModel(self):
        batches, specs = self._processDir()

        self._root = TreeNode(None, None)

        for batch in batches:
            newNode = TreeNode(batch, self._root)
            spec = specs.get(batch.name)
            if spec:
                for s in spec:
                    newNode.append_child(TreeNode(s, newNode))
            self._root.append_child(newNode)

    def _processDir(self):

        batches = list()
        specs_dict = dict()

        def checkFileEntry(entry):
            return entry.is_file() and entry.path.endswith('.xlsx') and 'ЗАПУСК' in entry.path

        def excelFiles():
            with os.scandir(self._workDir) as entries:
                for entry in entries:
                    if checkFileEntry(entry):
                        yield os.path.normpath(entry.path)

        for index, file in enumerate(excelFiles()):
            batch = Path(file).resolve().stem
            date_from_batch = batch[-7:].replace('_', '-')
            total_specs, needed_specs, specs_list = self._parseExcelFile(file=file)
            specs_received = sum(map(lambda el: int(el.is_received), specs_list))
            specs_dict[batch] = specs_list
            batches.append(BatchItem(rowid=index + 1, tier=StatTreeModel.TIER_1, name=batch, specs_needed=needed_specs,
                                     specs_total=total_specs, specs_received=specs_received,
                                     date=date_from_batch))

        return batches, specs_dict

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


    @property
    def workDir(self):
        return self._workDir

    @workDir.setter
    def workDir(self, name):
        if os.path.isdir(name):
            self._workDir = os.path.normpath(name)
            self.init()


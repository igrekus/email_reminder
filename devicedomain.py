import datetime
import os
import openpyxl

from pathlib import Path
from attr import attrs, attrib

from stattreemodel import StatTreeModel
from treenode import TreeNode


@attrs
class DeviceItem(object):
    _rowid = attrib(default=0, type=int)
    _tier = attrib(default=StatTreeModel.TIER_1)
    _name = attrib(default='', type=str)

    def __getitem__(self, item):
        if item == 0:
            return self.rowid
        elif item == 1:
            return self.name
        elif item == 2:
            return ''
        elif item == 3:
            return f'{3}/{4}'
        elif item == 'id':
            return self.rowid
        elif item == 'tier':
            return self.tier
        elif item == 'progress':
            return 3, 4
        elif item == 'received':
            return True

    @property
    def tier(self):
        return self._tier

    @property
    def name(self):
        return self._name

    @property
    def rowid(self):
        return self._rowid


@attrs
class RigTypeItem(object):
    _rowid = attrib(default=0, type=int)
    _tier = attrib(default=StatTreeModel.TIER_2)
    _name = attrib(default='', type=str)
    _desc = attrib(default='', type=str)
    _doc = attrib(default='', type=str)

    def __getitem__(self, item):
        if item == 0:
            return self.rowid
        elif item == 1:
            return self.name
        elif item == 2:
            return self.desc
        elif item == 3:
            return self.doc
        elif item == 'id':
            return self.rowid
        elif item == 'tier':
            return self.tier
        elif item == 'progress':
            return 1, 1
        elif item == 'received':
            return bool(self._doc)

    @property
    def tier(self):
        return self._tier

    @property
    def name(self):
        return self._name

    @property
    def desc(self):
        return self._desc

    @property
    def doc(self):
        return self._doc

    @property
    def rowid(self):
        return self._rowid


class DeviceDomain:

    def __init__(self):
        self._workDir = ''
        self._root = TreeNode(None, None)

    def init(self):
        print(f'init device domain for dir {self._workDir}')
        self._buildModel()

    def _buildModel(self):
        self._root = TreeNode(None, None)

        devices = [
            DeviceItem(0, 1, '1324B1Y'),
            DeviceItem(1, 1, '1324B2Y'),
            DeviceItem(2, 1, '1324B3Y')
        ]

        for dev in devices:
            newNode = TreeNode(dev, self._root)
            newNode.append_child(TreeNode(RigTypeItem(0, 2, 'Статика', 'ПП 23.10.1123', 'БКВП 111111.239841'), newNode))
            self._root.append_child(newNode)

        return
        # batches, specs = self._processDir()
        #
        # self._root = TreeNode(None, None)
        #
        # for file in batches:
        #     newNode = TreeNode(file, self._root)
        #     spec = specs.get(file.name)
        #     if spec:
        #         for s in spec:
        #             newNode.append_child(TreeNode(s, newNode))
        #     self._root.append_child(newNode)

    def _processDir(self):

        batches = list()
        specs_dict = dict()

        def checkFileEntry(entry):
            return entry.is_file() and entry.path.endswith('.xlsx')

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
            batches.append(DeviceItem(rowid=index + 1, tier=StatTreeModel.TIER_1, name=batch, specs_needed=needed_specs,
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
                    specs.append(RigTypeItem(rowid=rowid, name=f'{chip} - {desc}', developer=fio,
                                             is_received=False if is_received == '-' else True))
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

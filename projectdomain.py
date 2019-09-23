import datetime
import os
import openpyxl

from pathlib import Path
from attr import attrs, attrib

from stattreemodel import StatTreeModel
from treenode import TreeNode


@attrs
class ProjectItem(object):
    _rowid = attrib(default=0, type=int)
    _tier = attrib(default=StatTreeModel.TIER_1)
    _name = attrib(default='', type=str)

    def __getitem__(self, item):
        if item == 0:
            return self.rowid
        elif item == 1:
            return self.name
        elif item == 2:
            return 2
        elif item == 3:
            return f'{3}/{4}'
        elif item == 4:
            return '2019-06'
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
class DeviceItem(object):
    _rowid = attrib(default=0, type=int)
    _tier = attrib(default=StatTreeModel.TIER_2)
    _name = attrib(default='', type=str)

    def __getitem__(self, item):
        if item == 0:
            return self.rowid
        elif item == 1:
            return self.name
        elif item == 2:
            return 'stub total'
        elif item == 3:
            return 'stub progr'
        elif item == 4:
            return 'stub date'
        elif item == 'id':
            return self.rowid
        elif item == 'tier':
            return self.tier
        elif item == 'progress':
            return 1, 1
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

    def __getitem__(self, item):
        if item == 0:
            return self.rowid
        elif item == 1:
            return self.name
        elif item == 2:
            return 'stub total'
        elif item == 3:
            return '+'
        elif item == 4:
            return 'stub date'
        elif item == 'id':
            return self.rowid
        elif item == 'tier':
            return self.tier
        elif item == 'progress':
            return 1, 1
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


class ProjectDomain:

    def __init__(self):
        self._workDir = ''
        self._root = TreeNode(None, None)

    def init(self):
        print(f'init project domain for dir {self._workDir}')
        self._buildModel()

    def _buildModel(self):
        self._root = TreeNode(None, None)

        projects = [
            ProjectItem(0, 1, 'Преобразователь'),
            ProjectItem(1, 1, 'Высотка'),
            ProjectItem(2, 1, 'Дискрет')
        ]

        for proj in projects:
            tier1_node = TreeNode(proj, self._root)

            tier2_node = TreeNode(DeviceItem(0, 2, 'Устройство1'), tier1_node)
            tier2_node.append_child(TreeNode(RigTypeItem(0, 3, 'Статика'), tier2_node))

            tier1_node.append_child(tier2_node)

            self._root.append_child(tier1_node)

        return

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
            total_specs, needed_specs, specs_list = self._parseExcelFile(file=file)
            specs_dict[batch] = specs_list
            batches.append(DeviceItem(rowid=index + 1, tier=StatTreeModel.TIER_1, name=batch))

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
                    specs.append(RigTypeItem(rowid=rowid, name=f'{chip} - {desc}'))
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

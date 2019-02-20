# -*- coding: UTF-8 -*-

import re
from PyQt5.QtCore import QSortFilterProxyModel, Qt, QModelIndex, QVariant
from batchmodel import BatchModel


class DeviceSearchProxyModel(QSortFilterProxyModel):
    # TODO make generic proxy filter model

    def __init__(self, parent=None):
        super().__init__(parent)
        self.filterBatch = list()
        self.filterDeveloper = list()
        self.filterChip = list()
        self.filterDateCreateFrom = None
        self.filterDateCreateTo = None
        self.filterDateReceiveFrom = None
        self.filterDateReceiveTo = None
        self.filterNeeded = True
        self.filterNotNeeded = True
        self.filterReceived = True
        self.filterNotReceived = True
        self._filterString = ""
        self._filterRegex = re.compile(self._filterString, flags=re.IGNORECASE)
        self.cache = dict()

    def __setattr__(self, key, value):
        if key in self.__dict__ and key != "cache" and key != "_filterRegex":
            self.cache.clear()
        super().__setattr__(key, value)

    @property
    def filterString(self):
        return self._filterString

    @filterString.setter
    def filterString(self, string):
        if type(string) == str:
            self._filterString = string
            self._filterRegex = re.compile(string, flags=re.IGNORECASE)
        else:
            raise TypeError("Filter must be a str.")

    def filterAcceptsSelf(self, row, parent_index):

        def rowMatchesString():
            for i in range(self.sourceModel().columnCount()):
                string = str(self.sourceModel().index(row, i, parent_index).data(Qt.DisplayRole))
                if self._filterRegex.findall(string):
                    return True
            return False

        item_batch, item_developer, item_chip, item_date_create, item_date_receive, item_is_needed, item_is_received = \
            self.sourceModel().index(row, 0, parent_index).data(BatchModel.RoleFilterData)

        if not self.filterBatch or not self.filterDeveloper or not self.filterChip:
            return False

        if self.filterBatch and item_batch not in self.filterBatch:
            return False

        if self.filterDeveloper and item_developer not in self.filterDeveloper:
            return False

        if self.filterChip and item_chip not in self.filterChip:
            return False

        if self.filterDateCreateFrom is not None and self.filterDateCreateFrom > item_date_create:
            return False

        if self.filterDateCreateTo is not None and item_date_create > self.filterDateCreateTo:
            return False

        if self.filterDateReceiveFrom is not None and self.filterDateReceiveFrom > item_date_receive:
            return False

        if self.filterDateReceiveTo is not None and item_date_receive > self.filterDateReceiveTo:
            return False

        if not self.filterReceived and item_is_received:
            return False

        if not self.filterNotReceived and not item_is_received:
            return False

        if not self.filterNeeded and item_is_needed:
            return False

        if not self.filterNotNeeded and not item_is_needed:
            return False

        if self._filterString and not rowMatchesString():
            return False

        return True

    def filterAcceptsRow(self, source_row, source_parent_index):
        id_ = self.sourceModel().index(source_row, 0, source_parent_index).data(BatchModel.RoleNodeId)
        if id_ not in self.cache:
            self.cache[id_] = self.filterAcceptsSelf(source_row, source_parent_index)
        return self.cache[id_]

    def data(self, index, role=None):
        return super().data(index, role)

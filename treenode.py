class TreeNode(object):

    def __init__(self, data=None, parent=None):
        self._data = data
        self._parent_node = parent
        self._child_nodes = list()

    def __str__(self):
        return f'TreeNode(data:{self._data} parent:{self._parent_node} childs:{len(self._child_nodes)})'

    def __getitem__(self, item):
        return self._data[item]

    def append_child(self, item):
        self._child_nodes.append(item)

    def child_at(self, row):
        return self._child_nodes[row]

    def child_count(self):
        return len(self._child_nodes)

    def parent(self):
        return self._parent_node

    def row(self):
        if self._parent_node:
            return self._parent_node._child_nodes.index(self)
        return 0

    def has_child_nodes(self):
        return bool(self._child_nodes)

    def clear(self):
        for child in self._child_nodes:
            child.clear()
        self._child_nodes.clear()
        self._data = None
        self._parent_node = None

    @property
    def data(self):
        return self._data

    @data.setter
    def data(self, data):
        self._data = data

    @property
    def child_nodes(self):
        return self._child_nodes


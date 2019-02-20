class TreeNode:

    def __init__(self, data=None, parent=None):
        self._data = data or None
        self._child_nodes = list()
        self._parent_node = parent or None

    def __len__(self):
        return len(self._child_nodes)

    def append_child_node(self, item: 'TreeNode'):
        self._child_nodes.append(item)

    def child_node(self, row: int) -> 'TreeNode':
        return self._child_nodes[row]

    def child_node_count(self) -> int:
        return len(self._child_nodes)

    def parent(self) -> 'TreeNode':
        return self._parent_node

    def row(self) -> int:
        if not self._parent_node:
            return 0
        return self._parent_node._child_nodes.index(self)

    def has_child_nodes(self) -> bool:
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


import typing

from attr import attrs, Factory


@attrs(auto_attribs=True)
class TreeNode:

    _data: typing.Any = None
    _child_nodes: list = Factory(list)
    parent_node: typing.Optional['TreeNode'] = None
    column_count: int = 0

    def __len__(self) -> int:
        return len(self._child_nodes)

    def append_child_node(self, item: 'TreeNode'):
        self._child_nodes.append(item)

    def child_node(self, row: int) -> 'TreeNode':
        return self._child_nodes[row]

    def child_node_count(self) -> int:
        return len(self._child_nodes)

    def parent(self) -> 'TreeNode':
        return self.parent_node

    def row(self) -> int:
        if self.parent_node:
            return self.parent_node._child_nodes.index(self)
        return 0

    def has_child_nodes(self) -> bool:
        return bool(len(self._child_nodes))

    def clear(self):
        for child in self._child_nodes:
            child.clear()
        self._child_nodes.clear()
        self._data = None
        self.parent_node = None

    @property
    def data(self) -> typing.Any:
        return self._data

    @data.setter
    def data(self, data=typing.Any):
        self._data = data


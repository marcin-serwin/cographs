# pyright: strict
from abc import ABC, abstractmethod
from typing import Generic, Set, Optional, TypeVar, Any, List

VertexType = TypeVar("VertexType", covariant=True, bound=Any)
VT = VertexType


class TreeNode(ABC, Generic[VT]):
    def __init__(self):
        super().__init__()
        self.parent: Optional[InternalNode[VT]] = None

    @abstractmethod
    def degree(self) -> int:
        return 0

    def clear(self):
        pass


class LeafNode(TreeNode[VT]):
    def __init__(self, node: VT):
        super().__init__()
        self.node = node

    def degree(self) -> int:
        return 0

    def __repr__(self):
        return "LeafNode{{{}}}".format(self.node)


class InternalNode(TreeNode[VT]):
    def __init__(
            self,
            *,
            is_union: bool,
            children: Optional[Set[TreeNode[VT]]] = None):
        super().__init__()
        self.is_union = is_union
        self.children: Set[TreeNode[VT]
                           ] = children if children is not None else set()
        for child in self.children:
            child.parent = self
        self.marked_degree: int = 0
        self.processed_children: Set[TreeNode[VT]] = set()

    def add_child(self, *new_chilren: TreeNode[VT]):
        for new_child in new_chilren:
            new_child.parent = self
            self.children.add(new_child)

    def degree(self):
        return len(self.children)

    def clear(self):
        super().clear()
        self.marked_degree = 0
        self.processed_children = set()
        for child in self.children:
            child.clear()

    def __repr__(self):
        return "InternalNode{{{}, {}}}".format(
            "Union" if self.is_union else "Join", self.children)


class Path(List[VT]):
    def __hash__(self) -> int:
        return id(self)

# pyright: strict
from __future__ import annotations
from abc import ABC, abstractmethod
from typing import Generic, List, Set, Tuple, Optional, TypeVar, cast
from enum import Enum
import networkx as nx
from cographs.utilities import pick

# TODO: Remove bounding when typing bug is resolved
VertexType = TypeVar("VertexType", bound=str)
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


class MarkResult(Enum):
    ALL_MARKED = 0
    NONE_MARKED = 1
    SOME_MARKED = 2


def mark(new_node: LeafNode[VT],
         cotree_leaves: List[LeafNode[VT]],
         graph: nx.Graph[VT],
         root: InternalNode[VT]) -> Tuple[MarkResult, Set[InternalNode[VT]]]:
    root.clear()

    to_unmark: List[TreeNode[VT]] = []
    marked: Set[TreeNode[VT]] = set()
    for node in cotree_leaves:
        if graph.has_edge(node.node, new_node.node):
            marked.add(node)
            to_unmark.append(node)

    if len(marked) == 0:
        return (MarkResult.NONE_MARKED,
                cast(Set[InternalNode[VT]], marked))

    while len(to_unmark) > 0:
        node = to_unmark.pop()
        marked.remove(node)
        parent = node.parent
        if isinstance(node, InternalNode):
            node.marked_degree = 0
        if parent is not None:
            if parent not in marked:
                marked.add(parent)
            parent.marked_degree += 1
            if parent.marked_degree == parent.degree():
                to_unmark.append(parent)
            parent.processed_children.add(node)
    if len(marked) > 0 and root.degree() == 1:
        marked.add(root)

    assert all([isinstance(vertex, InternalNode)
                for vertex in marked])

    return (MarkResult.SOME_MARKED if len(marked) > 0
            else MarkResult.ALL_MARKED,
            cast(Set[InternalNode[VT]], marked))


def find_lowest(
        root: InternalNode[VT],
        marked: Set[InternalNode[VT]]) -> Optional[InternalNode[VT]]:
    invalid_node = None
    if root not in marked:
        return None

    if root.marked_degree != root.degree() - 1:
        invalid_node = root
    marked.remove(root)
    root.marked_degree = 0
    path_start = path_end = root

    while len(marked) > 0:
        path_start = marked.pop()
        if invalid_node is not None:
            return None
        if not path_start.is_union:
            if path_start.marked_degree != path_start.degree() - 1:
                invalid_node = path_start
            if path_start.parent in marked:
                return None
            assert path_start.parent is not None
            current = path_start.parent.parent
        else:
            invalid_node = path_start
            current = path_start.parent

        path_start.marked_degree = 0

        while current != path_end:
            assert current is not None
            if (current == root or
                    current not in marked or
                    current.marked_degree != current.degree() - 1 or
                    current.parent in marked):
                return None
            marked.remove(current)
            current.marked_degree = 0
            assert current.parent is not None
            current = current.parent.parent

        path_end = path_start
    return path_start


def updated_cotree(
        leaf: LeafNode[VT],
        lowest_marked: InternalNode[VT],
        root: InternalNode[VT]) -> InternalNode[VT]:
    children = (lowest_marked.processed_children
                if lowest_marked.is_union
                else lowest_marked.children - lowest_marked.processed_children)

    if len(children) == 1:
        child = pick(children)
        if isinstance(child, LeafNode):
            lowest_marked.children.remove(child)
            lowest_marked.add_child(InternalNode(
                is_union=not lowest_marked.is_union,
                children=set([child, leaf])))
        elif isinstance(child, InternalNode):
            child.add_child(leaf)
    else:
        lowest_marked.children -= lowest_marked.processed_children
        new_node = InternalNode(is_union=lowest_marked.is_union, children=set(
            lowest_marked.processed_children))
        if lowest_marked.is_union:
            lowest_marked.add_child(InternalNode(
                is_union=not lowest_marked.is_union,
                children=set([new_node, leaf])))
        else:
            if lowest_marked.parent is not None:
                lowest_marked.parent.children.remove(lowest_marked)
                lowest_marked.parent.add_child(new_node)
            else:
                root = new_node
                new_node.add_child(InternalNode(
                    is_union=True, children=set([lowest_marked, leaf])))

    return root


def compute_cotree(graph: nx.Graph[VT]) -> Optional[TreeNode[VT]]:
    leaves = [LeafNode(x) for x in graph.nodes]

    if graph.number_of_nodes() == 0:
        return None

    if graph.number_of_nodes() == 1:
        return pick(leaves)

    root: InternalNode[VT] = InternalNode(is_union=False)

    if graph.has_edge(leaves[0].node, leaves[1].node):
        root.add_child(*leaves[:2])
    else:
        root.add_child(InternalNode(is_union=True, children=set(leaves[:2])))

    for index, leaf in enumerate(leaves[2:], 2):
        result, marked = mark(leaf, leaves[:index], graph, root)
        if result == MarkResult.ALL_MARKED:
            root.add_child(leaf)
        elif result == MarkResult.NONE_MARKED:
            if root.degree() == 1:
                root_child = pick(root.children)
                assert isinstance(root_child, InternalNode)
                root_child.add_child(leaf)
            else:
                root = InternalNode(is_union=False, children=set(
                    [InternalNode(is_union=True, children=set([root, leaf]))]))
        else:
            lowest_marked = find_lowest(root, marked)
            if lowest_marked is None:
                return None
            root = updated_cotree(leaf, lowest_marked, root)

    return root


def is_cograph(graph: nx.Graph[VT]) -> bool:
    return compute_cotree(graph) is not None


def main():
    graph = nx.read_yaml("./graphs/example2.yaml")
    if is_cograph(graph):
        print("example is cograph")
    else:
        print("example contains a P4")


if __name__ == "__main__":
    main()

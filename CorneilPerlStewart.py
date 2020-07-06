from __future__ import annotations
from abc import ABC, abstractmethod
import networkx as nx
import itertools
from typing import List, Set
from enum import Enum


class TreeNode(ABC):
    def __init__(self, parent: InternalNode):
        self.parent = parent
        super().__init__()

    @abstractmethod
    def degree(self):
        pass

    def clear(self):
        pass


class LeafNode(TreeNode):
    def __init__(self, parent: InternalNode, node):
        self.node = node
        super().__init__(parent)

    def degree(self):
        return 0

    def __repr__(self):
        return "LeafNode{{{}}}".format(self.node)


class InternalNode(TreeNode):
    def __init__(
            self,
            parent: InternalNode,
            is_union: bool,
            children: List[TreeNode] = None):
        self.is_union = is_union
        self.children = children if children is not None else []
        self.marked_degree = 0
        self.marked_or_unmarked_children = []
        super().__init__(parent)

    def degree(self):
        return len(self.children)

    def clear(self):
        super().clear()
        self.marked_degree = 0
        self.marked_or_unmarked_children = []
        for child in self.children:
            child.clear()

    def __repr__(self):
        return "InternalNode{{{}, {}}}".format(
            "Union" if self.is_union else "Join", self.children)


class MarkResult(Enum):
    ALL_MARKED = 0
    NONE_MARKED = 1
    SOME_MARKED = 2


def mark(
        newNode: LeafNode,
        cotree_leaves: List[LeafNode],
        graph: nx.Graph,
        root: InternalNode) -> (MarkResult, Set[InternalNode]):
    root.clear()

    toUnmark = []
    nMarked = 0
    marked = set()
    for node in cotree_leaves:
        if graph.has_edge(node.node, newNode.node):
            marked.add(node)
            toUnmark.append(node)
            nMarked += 1

    if nMarked == 0:
        return (MarkResult.NONE_MARKED, marked)

    while len(toUnmark) > 0:
        node = toUnmark.pop()
        marked.remove(node)
        nMarked -= 1
        if isinstance(node, InternalNode):
            node.marked_degree = 0
        parent = node.parent
        if parent is not None:
            marked.add(parent)
            nMarked += 1
            parent.marked_degree += 1
            if parent.marked_degree == parent.degree():
                toUnmark.append(parent)
            parent.marked_or_unmarked_children.append(node)
    if nMarked > 0 and root.degree() == 1:
        marked.add(root)

    return (MarkResult.SOME_MARKED if nMarked >
            0 else MarkResult.ALL_MARKED, marked)


def findLowest(root: InternalNode, marked: Set[InternalNode]) -> InternalNode:
    y = None
    if root not in marked:
        return None

    if root.marked_degree != root.degree() - 1:
        y = root
    marked.remove(root)
    root.marked_degree = 0
    u = w = root

    while len(marked) > 0:
        u = marked.pop()
        if y is not None:
            return None
        if not u.is_union:
            if u.marked_degree != u.degree() - 1:
                y = u
            if u.parent in marked:
                return None
            else:
                t = u.parent.parent
        else:
            y = u
            t = u.parent

        u.marked_degree = 0

    return u


def computeCotree(graph: nx.Graph) -> TreeNode:
    leaves = [LeafNode(None, x) for x in graph.nodes]

    if graph.number_of_nodes() == 0:
        return None

    if graph.number_of_nodes() == 1:
        return leaves[0]

    root = InternalNode(None, False)

    if graph.has_edge(leaves[0].node, leaves[1].node):
        for leaf in leaves[:2]:
            leaf.parent = root
        root.children = leaves[:2]
    else:
        node = InternalNode(root, True, leaves[:2])
        for leaf in leaves[:2]:
            leaf.parent = node
        root.children = [node]

    for index, leaf in enumerate(leaves[2:]):
        result, marked = mark(leaf, leaves[:index], graph, root)
        if result == MarkResult.ALL_MARKED:
            leaf.parent = root
            root.children.append(leaf)
        elif result == MarkResult.NONE_MARKED:
            if root.degree() == 1:
                root_child = root.children[0]
                leaf.parent = root_child
                root_child.children.append(leaf)
            else:
                new_root_child = InternalNode(None, True, [root, leaf])
                root.parent = new_root_child
                leaf.parent = new_root_child

                root = InternalNode(None, False, [new_root_child])
                new_root_child.parent = root
        else:
            u = findLowest(root, marked)

    return root


if __name__ == "__main__":
    graph = nx.read_yaml("./graphs/example2.yaml")
    cotree = computeCotree(graph)
    print(cotree)
    # if isCograph(graph, partition):
    #     print('example is cograph')
    # else:
    #     print('example contains a P4')

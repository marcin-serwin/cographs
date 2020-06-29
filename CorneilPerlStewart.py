from abc import ABC, abstractmethod
import networkx as nx
import itertools
from typing import List
from enum import Enum


class TreeNode(ABC):
    def __init__(self, parent):
        self.parent = parent
        self.is_marked = False
        super().__init__()

    @abstractmethod
    def degree(self):
        pass

    def clear(self):
        self.is_marked = False


class LeafNode(TreeNode):
    def __init__(self, parent, node):
        self.node = node
        super().__init__(parent)

    def degree(self):
        return 0

    def __repr__(self):
        return "LeafNode{{{}}}".format(self.node)


class InternalNode(TreeNode):
    def __init__(self, parent, is_union, children=None):
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
        root: TreeNode) -> MarkResult:
    root.clear()

    toUnmark = []
    nMarked = 0
    for node in cotree_leaves:
        if graph.has_edge(node.node, newNode.node):
            node.is_marked = True
            toUnmark.append(node)
            nMarked += 1

    if nMarked == 0:
        return MarkResult.NONE_MARKED

    while len(toUnmark) > 0:
        node = toUnmark.pop()
        node.is_marked = False
        nMarked -= 1
        if isinstance(node, InternalNode):
            node.marked_degree = 0
        parent = node.parent
        if parent is not None:
            parent.is_marked = True
            nMarked += 1
            parent.marked_degree += 1
            if parent.marked_degree == parent.degree():
                toUnmark.append(parent)
            parent.marked_or_unmarked_children.append(node)
    if nMarked > 0 and root.degree() == 1:
        root.is_marked = True

    return MarkResult.SOME_MARKED if nMarked > 0 else MarkResult.ALL_MARKED


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
        result = mark(leaf, leaves[:index], graph, root)
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
            pass

    return root


if __name__ == "__main__":
    graph = nx.read_yaml("./graphs/example2.yaml")
    cotree = computeCotree(graph)
    print(cotree)
    # if isCograph(graph, partition):
    #     print('example is cograph')
    # else:
    #     print('example contains a P4')

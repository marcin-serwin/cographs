from abc import ABC, abstractmethod
import networkx as nx
import itertools
from typing import List


class TreeNode(ABC):
    def __init__(self, parent):
        self.parent = parent
        self.is_marked = False
        super().__init__()

    @abstractmethod
    def degree(self):
        pass


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

    def __repr__(self):
        return "InternalNode{{{}, {}}}".format(
            "Union" if self.is_union else "Join", self.children)


def mark(
        newNode: LeafNode,
        cotree_leaves: List[LeafNode],
        graph: nx.Graph,
        root: TreeNode):
    toUnmark = []
    nMarked = 0
    for node in cotree_leaves:
        if graph.has_edge(node.node, newNode.node):
            node.is_marked = True
            toUnmark.append(node)
            nMarked += 1

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


def computeCotree(graph: nx.Graph) -> TreeNode:
    leaves = [LeafNode(None, x) for x in graph.nodes]

    if graph.number_of_nodes() == 0:
        return None

    if graph.number_of_nodes() == 1:
        return leaves[0]

    cotree = InternalNode(None, False)

    if graph.has_edge(leaves[0].node, leaves[1].node):
        for leaf in leaves[:2]:
            leaf.parent = cotree
        cotree.children = leaves[:2]
    else:
        node = InternalNode(cotree, True, leaves[:2])
        for leaf in leaves[:2]:
            leaf.parent = node
        cotree.children = [node]

    for index, leaf in enumerate(leaves[2:]):
        mark(leaf, leaves[:index], graph, cotree)

    return cotree


if __name__ == "__main__":
    graph = nx.read_yaml("./graphs/example2.yaml")
    cotree = computeCotree(graph)
    print(cotree)
    # if isCograph(graph, partition):
    #     print('example is cograph')
    # else:
    #     print('example contains a P4')

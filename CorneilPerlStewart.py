from __future__ import annotations
from abc import ABC, abstractmethod
import networkx as nx
import itertools
from typing import List, Set
from enum import Enum
from utilities import pickFromSet


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
            children: Set[TreeNode] = None):
        self.is_union = is_union
        self.children = children if children is not None else set()
        for child in self.children:
            child.parent = self
        self.marked_degree = 0
        self.marked_or_unmarked_children = set()
        super().__init__(parent)

    def addChild(self, *newChilren: TreeNode):
        for newChild in newChilren:
            newChild.parent = self
            self.children.add(newChild)

    def degree(self):
        return len(self.children)

    def clear(self):
        super().clear()
        self.marked_degree = 0
        self.marked_or_unmarked_children = set()
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
            if parent not in marked:
                marked.add(parent)
                nMarked += 1
            parent.marked_degree += 1
            if parent.marked_degree == parent.degree():
                toUnmark.append(parent)
            parent.marked_or_unmarked_children.add(node)
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
    pathStart = pathEnd = root

    while len(marked) > 0:
        pathStart = marked.pop()
        if y is not None:
            return None
        if not pathStart.is_union:
            if pathStart.marked_degree != pathStart.degree() - 1:
                y = pathStart
            if pathStart.parent in marked:
                return None
            else:
                current = pathStart.parent.parent
        else:
            y = pathStart
            current = pathStart.parent

        pathStart.marked_degree = 0

        while current != pathEnd:
            if (current == root or current not in marked or current.marked_degree !=
                    current.degree() - 1 or current.parent in marked):
                return None
            marked.remove(current)
            current.marked_degree = 0
            current = current.parent.parent

        pathEnd = pathStart
    return pathStart


def updateCotree(
        leaf: LeafNode,
        lowestMarked: InternalNode,
        root: InternalNode):
    children = lowestMarked.marked_or_unmarked_children if lowestMarked.is_union else lowestMarked.children - \
        lowestMarked.marked_or_unmarked_children

    if len(children) == 1:
        child = pickFromSet(children)
        if isinstance(child, LeafNode):
            lowestMarked.children.remove(child)
            lowestMarked.children.add(InternalNode(
                lowestMarked, not lowestMarked.is_union, set([child, leaf])))
        else:
            child.addChild(leaf)
    else:
        lowestMarked.children -= lowestMarked.marked_or_unmarked_children
        newNode = InternalNode(
            None, lowestMarked.is_union, set(
                lowestMarked.marked_or_unmarked_children))
        if lowestMarked.is_union:
            lowestMarked.addChild(InternalNode(
                None, not lowestMarked.is_union, set([newNode, leaf])))
        else:
            if lowestMarked.parent is not None:
                lowestMarked.parent.children.remove(lowestMarked)
                lowestMarked.parent.addChild(newNode)
            else:
                root = newNode
                newNode.addChild(InternalNode(
                    None, True, set([lowestMarked, leaf])))


def computeCotree(graph: nx.Graph) -> TreeNode:
    leaves = [LeafNode(None, x) for x in graph.nodes]

    if graph.number_of_nodes() == 0:
        return None

    if graph.number_of_nodes() == 1:
        return leaves[0]

    root = InternalNode(None, False)

    if graph.has_edge(leaves[0].node, leaves[1].node):
        root.addChild(*leaves[:2])
    else:
        root.addChild(InternalNode(root, True, set(leaves[:2])))

    for index, leaf in enumerate(leaves[2:], 2):
        result, marked = mark(leaf, leaves[:index], graph, root)
        if result == MarkResult.ALL_MARKED:
            root.addChild(leaf)
        elif result == MarkResult.NONE_MARKED:
            if root.degree() == 1:
                root_child = pickFromSet(root.children)
                root_child.addChild(leaf)
            else:
                root = InternalNode(None, False, set(
                    [InternalNode(None, True, set([root, leaf]))]))
        else:
            lowestMarked = findLowest(root, marked)
            if lowestMarked is None:
                return None
            updateCotree(leaf, lowestMarked, root)

    return root


if __name__ == "__main__":
    graph = nx.read_yaml("./graphs/example2.yaml")
    cotree = computeCotree(graph)
    print(cotree)
    if cotree is not None:
        print('example is cograph')
    else:
        print('example contains a P4')

from abc import ABC
import networkx as nx
import itertools


class TreeNode(ABC):
    pass


class LeafNode(TreeNode):
    def __init__(self, node):
        self.node = node

    def __repr__(self):
        return "LeafNode{{{}}}".format(self.node)


class InternalNode(TreeNode):
    def __init__(self, isUnion, children=None):
        self.isUnion = isUnion
        self.children = children if children is not None else []

    def __repr__(self):
        return "InternalNode{{{}, {}}}".format(
            "Union" if self.isUnion else "Join", self.children)


def getNode(nodes):
    for node in nodes:
        return node


def computeCotree(graph: nx.Graph) -> TreeNode:
    leaves = [LeafNode(x) for x in graph.nodes]

    if graph.number_of_nodes() == 0:
        return None

    if graph.number_of_nodes() == 1:
        return leaves[0]

    cotree = InternalNode(False)

    if graph.has_edge(leaves[0].node, leaves[1].node):
        cotree.children = leaves[:2]
    else:
        cotree.children = [InternalNode(True, leaves[:2])]

    for leaf in leaves[2:]:
        pass

    return cotree


if __name__ == "__main__":
    graph = nx.read_yaml("./graphs/example2.yaml")
    cotree = computeCotree(graph)
    print(cotree)
    # if isCograph(graph, partition):
    #     print('example is cograph')
    # else:
    #     print('example contains a P4')

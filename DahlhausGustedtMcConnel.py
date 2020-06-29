import networkx as nx
import itertools


class TreeNode(object):
    def __init__(self, node):
        self.node = node


def restrictStep():
    pass


def computeModularDecomposition(graph: nx.Graph) -> TreeNode:
    if graph.number_of_nodes() == 0:
        return None

    print(list(graph.nodes), graph.number_of_nodes())
    for node in list(graph.nodes):
        break

    print(node)
    if graph.number_of_nodes() == 1:
        return TreeNode(node)

    neighbors = set(graph.neighbors(node))
    notNeighbors = graph.nodes - neighbors - set([node])

    neighborsDecomposition = computeModularDecomposition(
        graph.subgraph(neighbors))
    notNeighborsDecomposition = computeModularDecomposition(
        graph.subgraph(notNeighbors))

    restrictStep()

    return neighborsDecomposition


if __name__ == "__main__":
    graph = nx.read_yaml("./graphs/example2.yaml")
    decomposition = computeModularDecomposition(graph)
    print(decomposition)
    # if isCograph(graph, partition):
    #     print('example is cograph')
    # else:
    #     print('example contains a P4')

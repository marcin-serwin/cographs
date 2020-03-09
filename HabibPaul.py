import networkx as nx
import itertools


def bruteForcePartition(graph: nx.Graph) -> list:
    partition = [set(graph.nodes)]

    while any(len(part) > 1 for part in partition):
        index, part = next(
            filter(lambda p: len(p[1]) > 1, enumerate(partition)))
        origin = part.pop()

        neighbors = set(graph.neighbors(origin)) & part
        notNeighbors = part - neighbors

        right = [neighbors]

        for y in notNeighbors:
            y_neighbors = set(graph.neighbors(y))
            right = [s for s in itertools.chain.from_iterable(
                [subPart - y_neighbors, subPart & y_neighbors] for subPart in right) if len(s) > 0]

        left = [notNeighbors]

        for sp in right:
            for y in sp:
                break
            y_neighbors = set(graph.neighbors(y))
            left = [s for s in itertools.chain.from_iterable(
                [subPart - y_neighbors, subPart & y_neighbors] for subPart in left) if len(s) > 0]

        refined = [*left, set([origin]), *right]

        partition = [*partition[:index], *refined, *partition[index + 1:]]

    return [s.pop() for s in partition]


def areTheseTwins(graph: nx.Graph, partition: list, x: any, y: any) -> bool:
    if x is None or y is None:
        return False

    x_neighbors = set(graph.neighbors(x)) & set(partition)
    y_neighbors = set(graph.neighbors(y)) & set(partition)

    return x_neighbors == y_neighbors or (
        x_neighbors | set([x])) == (y_neighbors | set([y]))


def isCograph(graph: nx.Graph, partition: list) -> bool:
    partition = [None, *partition, None]

    z = 1
    while z + 1 != len(partition):
        prec = partition[z - 1]
        curr = partition[z]
        succ = partition[z + 1]

        if areTheseTwins(graph, partition, curr, prec):
            z -= 1
            del partition[z]
        elif areTheseTwins(graph, partition, curr, succ):
            del partition[z]
        else:
            z += 1

    return len(partition) == 3


if __name__ == "__main__":
    graph = nx.read_yaml("./graphs/example.yaml")
    partition = bruteForcePartition(graph)
    if isCograph(graph, partition):
        print('example is cograph')
    else:
        print('example contains a P4')

import networkx as nx
import itertools


def bruteForcePartition(graph: nx.Graph):
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


if __name__ == "__main__":
    print(bruteForcePartition(nx.read_yaml("./graphs/example.yaml")))

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


class Part(object):
    def __init__(self, vertices):
        self.vertices = set(vertices)
        self.pivot = None


def first_refinement_rule(
        graph: nx.Graph, origin_part: Part, origin) -> (list, list, list):
    origin_part.vertices.remove(origin)
    neighbors = Part(set(graph[origin]) & origin_part.vertices)
    notNeighbors = Part(origin_part.vertices - neighbors.vertices)
    origin_part = Part([origin])

    return notNeighbors, origin_part, neighbors


def second_refinement_rule(
        graph: nx.Graph,
        part: Part,
        unused_parts: list,
        partition: list) -> list:
    neighbors = set(graph[part.pivot])
    notNeighbors = graph.nodes - neighbors
    notNeighbors.remove(part.pivot)

    new_partition = []
    for part_prime in partition:
        if len(part_prime.vertices) <= 1 or part == part_prime:
            new_partition.append(part_prime)
        else:
            l, r = (Part(part_prime.vertices & notNeighbors),
                    Part(part_prime.vertices & neighbors))

            new_partition.extend(
                (x for x in (l, r) if len(x.vertices) > 0))
            unused_parts.extend(
                (x for x in (l, r) if len(x.vertices) > 0))

    return new_partition


def get_new_origin_index(origin_part: Part, partition: list) -> int:
    z_l_index, z_r_index = None, None
    pastOrigin = False
    for index, part in enumerate(partition):
        if len(part.vertices) == 1 and part == origin_part:
            pastOrigin = True
        elif len(part.vertices) > 1:
            if pastOrigin and part.pivot is not None:
                z_r_index = index
                break
            elif not pastOrigin and part.pivot is not None:
                z_l_index = index

    if z_l_index is None:
        return z_r_index
    elif z_r_index is None:
        return z_l_index
    elif partition[z_l_index].pivot in graph[partition[z_r_index].pivot]:
        return z_l_index
    else:
        return z_r_index


def computePermutation(g: nx.Graph) -> list:
    graph = nx.Graph(g)

    origin = None
    uninterestingVertices = []
    for node in list(graph.nodes):
        if len(graph[node]) in [len(graph.nodes) - 1, 0]:
            uninterestingVertices.append(node)
            graph.remove_node(node)
        else:
            origin = node
            break

    if origin is None:
        return uninterestingVertices

    partition = [Part(graph.nodes)]
    origin_part_index = 0
    unused_parts = []

    while any(len(part.vertices) > 1 for part in partition):
        origin_part = partition[origin_part_index]

        if len(origin_part.vertices) > 1:
            notNeighbors, origin_part, neighbors = first_refinement_rule(
                graph, origin_part, origin)

            partition = [*partition[:origin_part_index], notNeighbors,
                         origin_part, neighbors, *partition[origin_part_index + 1:]]

            unused_parts.extend(
                p for p in (neighbors, notNeighbors) if len(p.vertices) > 0)

        while len(unused_parts) > 0:
            part = unused_parts.pop()
            for vertex in part.vertices:
                break
            part.pivot = vertex

            partition = second_refinement_rule(
                graph, part, unused_parts, partition)

        origin_part_index = get_new_origin_index(origin_part, partition)

        if origin_part_index is None:
            break
        origin = partition[origin_part_index].pivot

    return uninterestingVertices + [p.vertices.pop()
                                    for p in partition if len(p.vertices) > 0]


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
        prec, curr, succ = partition[z - 1:z + 2]

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
    partition = computePermutation(graph)
    if isCograph(graph, partition):
        print('example is cograph')
    else:
        print('example contains a P4')

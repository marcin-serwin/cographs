# pyright: strict
from __future__ import annotations
from dataclasses import dataclass
import itertools
from typing import Generic, Optional, Tuple, Set, List
import networkx as nx
from cographs.cotree_classes import VT
from cographs.utilities import pick


def brute_force_partition(graph: nx.Graph[VT]) -> List[VT]:
    partition = [set(graph.nodes)]

    while any(len(part) > 1 for part in partition):
        index, part = next(
            filter(lambda p: len(p[1]) > 1, enumerate(partition)))
        origin = part.pop()

        neighbors = set(graph.neighbors(origin)) & part
        not_neighbors = part - neighbors

        right = [neighbors]

        for node in not_neighbors:
            node_neighbors = set(graph.neighbors(node))
            right = [s for s in itertools.chain.from_iterable(
                [sub_part - node_neighbors, sub_part & node_neighbors]
                for sub_part in right) if len(s) > 0]

        left = [not_neighbors]

        for sub_part in right:
            node = pick(sub_part)
            node_neighbors = set(graph.neighbors(node))
            left = [s for s in itertools.chain.from_iterable(
                [sub_part - node_neighbors, sub_part & node_neighbors]
                for sub_part in left) if len(s) > 0]

        refined = left + [set([origin])] + right

        partition = partition[:index] + refined + partition[index + 1:]

    return [s.pop() for s in partition]


@dataclass
class Part(Generic[VT]):
    vertices: Set[VT]
    pivot: VT = None

    def __hash__(self) -> int:
        return id(self)


def first_refinement_rule(
        graph: nx.Graph[VT],
        origin_part: Part[VT],
        origin: VT) -> Tuple[Part, Part, Part]:
    origin_part.vertices.remove(origin)
    neighbors = Part(set(graph[origin]) & origin_part.vertices)
    not_neighbors = Part(origin_part.vertices - neighbors.vertices)
    origin_part = Part(set([origin]))

    return not_neighbors, origin_part, neighbors


def second_refinement_rule(
        graph: nx.Graph[VT],
        part: Part[VT],
        unused_parts: Set[VT],
        partition: List[VT]) -> List[VT]:
    pivot_set = set(graph[part.pivot])
    neighbors = set(graph[part.pivot])
    not_neighbors = set(graph.nodes - neighbors)
    not_neighbors.remove(part.pivot)

    new_partition = []

    for part_prime in partition:
        if len(part_prime.vertices) <= 1 or part == part_prime:
            new_partition.append(part_prime)
            continue

        left, right = (Part(part_prime.vertices - pivot_set),
                       Part(part_prime.vertices & pivot_set))

        if len(left.vertices) == 0 or len(right.vertices) == 0:
            new_partition.append(part_prime)
            continue

        new_partition.extend(x for x in (left, right))
        if part_prime in unused_parts:
            unused_parts.remove(part_prime)
            unused_parts.add(left)
            unused_parts.add(right)
        else:
            old, new = ((left, right)
                        if part_prime.pivot in left.vertices
                        else (right, left))
            old.pivot = part_prime.pivot
            unused_parts.add(new)

    return new_partition


def get_new_origin_index(
        origin_part: Part[VT],
        partition: List[VT],
        graph: nx.Graph[VT]) -> Optional[int]:
    z_l_index: Optional[int] = None
    z_r_index: Optional[int] = None
    past_origin = False
    for index, part in enumerate(partition):
        if part == origin_part:
            past_origin = True
        elif len(part.vertices) > 1:
            if past_origin and part.pivot is not None:
                z_r_index = index
                break
            if not past_origin and part.pivot is not None:
                z_l_index = index

    if z_l_index is None:
        return z_r_index
    if z_r_index is None:
        return z_l_index
    if partition[z_l_index].pivot in graph[partition[z_r_index].pivot]:
        return z_l_index
    return z_r_index


def compute_permutation(graph: nx.Graph[VT]) -> List[VT]:
    graph = nx.Graph(graph)

    origin = None
    uninteresting_vertices = []
    for node in list(graph.nodes):
        if len(graph[node]) in [len(graph.nodes) - 1, 0]:
            uninteresting_vertices.append(node)
            graph.remove_node(node)
        else:
            origin = node
            break

    if origin is None:
        return uninteresting_vertices

    partition = [Part(set(graph.nodes), origin)]
    origin_part_index = 0
    unused_parts = set()

    while origin_part_index is not None:
        origin_part = partition[origin_part_index]
        origin = origin_part.pivot

        if len(origin_part.vertices) > 1:
            not_neighbors, origin_part, neighbors = first_refinement_rule(
                graph, origin_part, origin)

            partition = (partition[:origin_part_index] +
                         [x for x in [not_neighbors, origin_part, neighbors]
                          if len(x.vertices) > 0] +
                         partition[origin_part_index + 1:])

            for part in (neighbors, not_neighbors):
                if len(part.vertices) > 0:
                    unused_parts.add(part)
        while len(unused_parts) > 0:
            part = unused_parts.pop()
            vertex = pick(part.vertices)
            part.pivot = vertex

            partition = second_refinement_rule(
                graph, part, unused_parts, partition)

        origin_part_index = get_new_origin_index(origin_part, partition, graph)

    return uninteresting_vertices + [p.vertices.pop()
                                     for p in partition if len(p.vertices) > 0]


def are_these_twins(
        graph: nx.Graph[VT],
        partition: List[VT],
        lhs: Optional[VT],
        rhs: Optional[VT]) -> bool:
    if lhs is None or rhs is None:
        return False

    x_neighbors = set(graph.neighbors(lhs)) & set(partition)
    y_neighbors = set(graph.neighbors(rhs)) & set(partition)

    return x_neighbors == y_neighbors or (
        x_neighbors | set([lhs])) == (y_neighbors | set([rhs]))


def check_partition(graph: nx.Graph[VT], partition: List[VT]) -> bool:
    partition = [None, *partition, None]

    position = 1
    while position + 1 != len(partition):
        prec, curr, succ = partition[position - 1:position + 2]

        if are_these_twins(graph, partition, curr, prec):
            position -= 1
            del partition[position]
        elif are_these_twins(graph, partition, curr, succ):
            del partition[position]
        else:
            position += 1

    return len(partition) == 3


def is_cograph(graph: nx.Graph[VT]):
    return check_partition(graph, compute_permutation(graph))

# pyright: strict
from __future__ import annotations
from typing import Set, List
from itertools import accumulate, combinations, product
import networkx as nx
from cographs.cotree_classes import VT, Path


def is_independent_set(graph: nx.Graph[VT], independent_set: Set[VT]) -> bool:
    for v_1, v_2 in combinations(independent_set, 2):
        if graph.has_edge(v_1, v_2):
            return False
    return True


def independent_set_of_size_exists(graph: nx.Graph[VT], size: int) -> bool:
    for independent_set in combinations(graph.nodes, size):
        if is_independent_set(graph, set(independent_set)):
            return True
    return False


def is_max_independent_set(
        graph: nx.Graph[VT],
        independent_set: Set[VT]) -> bool:
    return (
        is_independent_set(graph, independent_set) and
        not independent_set_of_size_exists(graph, len(independent_set) - 1))


def is_clique(graph: nx.Graph[VT], clique: Set[VT]) -> bool:
    for v_1, v_2 in combinations(clique, 2):
        if not graph.has_edge(v_1, v_2):
            return False
    return True


def clique_of_size_exists(graph: nx.Graph[VT], size: int) -> bool:
    for clique in combinations(graph.nodes, size):
        if is_clique(graph, set(clique)):
            return True
    return False


def is_max_clique(
        graph: nx.Graph[VT],
        clique: Set[VT]) -> bool:
    return (
        is_clique(graph, clique) and
        not clique_of_size_exists(graph, len(clique) - 1))


def is_coloring(graph: nx.Graph[VT], coloring: List[Set[VT]]) -> bool:
    coverage = reduce(lambda x, y: x | y, coloring)
    if len(coverage) != len(graph.nodes):
        return False
    for color in coloring:
        for v_1, v_2 in combinations(color, 2):
            if graph.has_edge(v_1, v_2):
                return False
    return True


def is_graph_colorable_with(
        graph: nx.Graph[VT],
        number_of_colors: int) -> bool:
    nodes = list(graph.nodes)

    for node_colors in product(range(number_of_colors), repeat=len(nodes)):
        coloring: List[Set[VT]] = [set()] * number_of_colors
        for node, color in zip(nodes, node_colors):
            coloring[color].add(node)
        if is_coloring(graph, coloring):
            return True
    return False


def is_optimal_coloring(graph: nx.Graph[VT], coloring: List[Set[VT]]) -> bool:
    return (is_coloring(graph, coloring) and
            not is_graph_colorable_with(graph, len(coloring) - 1))


def is_path_cover(graph: nx.Graph[VT], path_cover: Set[Path[VT]]):
    if len(list(accumulate(
            path_cover,
            lambda x, y: x + y))) != len(graph.nodes):
        return False
    for path in path_cover:
        for v_1, v_2 in zip(path, path[1:]):
            if not graph.has_edge(v_1, v_2):
                return False
    return True

# pyright: strict
from __future__ import annotations
from dataclasses import dataclass
from itertools import product
from functools import reduce
from typing import Callable, TypeVar, Set, List
import networkx as nx
from cographs.cotree_classes import InternalNode, LeafNode, TreeNode, VT, Path

TraversalResult = TypeVar("TraversalResult")
TR = TraversalResult


@dataclass
class CotreeAlgorithm:
    merge_union: Callable[[TR, TR], TR]
    merge_join: Callable[[TR, TR], TR]
    handle_leaf: Callable[[LeafNode[VT]], TR]


def traverse_cotree(root: TreeNode[VT], algorithm: CotreeAlgorithm) -> TR:
    if isinstance(root, LeafNode):
        return algorithm.handle_leaf(root)
    assert isinstance(root, InternalNode)

    return reduce(
        algorithm.merge_union if root.is_union else algorithm.merge_join,
        (traverse_cotree(child, algorithm) for child in root.children),
    )


def reconstruct_graph(cotree: TreeNode[VT]) -> nx.Graph[VT]:
    def join_graphs(lhs: nx.Graph[VT], rhs: nx.Graph[VT]) -> nx.Graph[VT]:
        graph = nx.union(lhs, rhs)
        for edge in product(lhs.nodes, rhs.nodes):
            graph.add_edge(*edge)
        return graph

    def trivial_graph(node: VT) -> nx.Graph[VT]:
        graph: nx.Graph[VT] = nx.Graph()
        graph.add_node(node)
        return graph

    return traverse_cotree(cotree, CotreeAlgorithm(
        nx.union,
        join_graphs,
        lambda leaf: trivial_graph(leaf.node)
    ))


def find_max_clique(cotree: TreeNode[VT]) -> Set[VT]:
    def pick_max(lhs: Set[VT], rhs: Set[VT]) -> Set[VT]:
        return lhs if len(lhs) >= len(rhs) else rhs

    def join_cliques(lhs: Set[VT], rhs: Set[VT]) -> Set[VT]:
        return lhs | rhs

    def trivial_graph(leaf: LeafNode[VT]) -> Set[VT]:
        return set([leaf.node])

    return traverse_cotree(cotree, CotreeAlgorithm(
        pick_max,
        join_cliques,
        trivial_graph
    ))


def find_max_independent_set(cotree: TreeNode[VT]) -> Set[VT]:
    def join_independent_sets(lhs: Set[VT], rhs: Set[VT]) -> Set[VT]:
        return lhs | rhs

    def pick_max(lhs: Set[VT], rhs: Set[VT]) -> Set[VT]:
        return lhs if len(lhs) >= len(rhs) else rhs

    def trivial_graph(leaf: LeafNode[VT]) -> Set[VT]:
        return set([leaf.node])

    return traverse_cotree(cotree, CotreeAlgorithm(
        join_independent_sets,
        pick_max,
        trivial_graph
    ))


def find_min_coloring(cotree: TreeNode[VT]) -> List[Set[VT]]:
    def union_colorings(
            lhs: List[Set[VT]], rhs: List[Set[VT]]) -> List[Set[VT]]:
        if len(lhs) > len(rhs):
            rhs += (len(lhs) - len(rhs)) * [set()]
        else:
            lhs += (len(rhs) - len(lhs)) * [set()]
        return [x | y for x, y in zip(lhs, rhs)]

    def join_colorings(lhs: List[Set[VT]],
                       rhs: List[Set[VT]]) -> List[Set[VT]]:
        return lhs + rhs

    def trivial_graph(leaf: LeafNode[VT]) -> List[Set[VT]]:
        return [set([leaf.node])]

    return traverse_cotree(cotree, CotreeAlgorithm(
        union_colorings,
        join_colorings,
        trivial_graph
    ))


def find_min_path_cover(cotree: TreeNode[VT]) -> Set[Path[VT]]:
    def union_min_paths(
            lhs: Set[Path[VT]], rhs: Set[Path[VT]]) -> Set[Path[VT]]:
        return lhs | rhs

    def join_min_paths(lhs: Set[Path[VT]],
                       rhs: Set[Path[VT]]) -> Set[Path[VT]]:
        smaller, bigger = (lhs, rhs) if len(lhs) <= len(rhs) else (rhs, lhs)
        path: Path[VT] = Path(bigger.pop())

        for path_prime in smaller:
            path += path_prime
            if len(bigger) > 0:
                path += bigger.pop()
        return bigger | set([path])

    def trivial_graph(leaf: LeafNode[VT]) -> Set[Path[VT]]:
        return set([Path([leaf.node])])

    return traverse_cotree(cotree, CotreeAlgorithm(
        union_min_paths,
        join_min_paths,
        trivial_graph
    ))

# pyright: strict
from __future__ import annotations
from dataclasses import dataclass
from itertools import product
from functools import reduce
from typing import Callable, TypeVar
import networkx as nx
from cographs.cotree_classes import InternalNode, LeafNode, TreeNode, VT

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

# pyright: strict
from __future__ import annotations
from dataclasses import dataclass
from itertools import product, chain
from functools import reduce
from typing import Callable, TypeVar, Set, List, Dict
import networkx as nx
from cographs.cotree_classes import InternalNode, LeafNode, TreeNode, VT, Path
from cographs.utilities import flatten, pick, singleton

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


def _mend_and_merge(leaves: Set[VT], paths: Set[Path[VT]]) -> Set[Path[VT]]:
    path = paths.pop()
    paths_vertex_size = sum(len(path) for path in paths)
    while len(leaves) > 0 and paths_vertex_size >= len(leaves):
        joined_path = paths.pop()
        path.append(leaves.pop())
        path.extend(joined_path)
        paths_vertex_size -= len(joined_path)
    if len(leaves) == 0:
        paths.add(path)
        return paths
    else:
        path, tail = (path[:-(len(leaves) - paths_vertex_size)],
                      path[-(len(leaves) - paths_vertex_size):])
        paths.add(Path(tail))
        path.extend(flatten(zip(chain.from_iterable(paths), leaves)))
        return singleton(Path(path))


def _find_min_path_cover(
        root: TreeNode[VT], leaves: Dict[int, Set[VT]]) -> Set[Path[VT]]:
    if isinstance(root, LeafNode):
        return set([Path([root.node])])
    assert isinstance(root, InternalNode)
    if root.is_union:
        return reduce(
            lambda x, y: x | y,
            (find_min_path_cover(child) for child in root.children))
    else:
        child = pick(root.children)
        if len(root.children) == 1:
            return _find_min_path_cover(child, leaves)
        child_leaves = leaves[id(child)]
        if len(child_leaves) > len(leaves[id(root)]) - len(child_leaves):
            return _mend_and_merge(leaves[id(root)] - child_leaves,
                                   _find_min_path_cover(child, leaves))
        else:
            root.children.remove(child)
            leaves[id(root)] -= child_leaves
            result = _mend_and_merge(child_leaves,
                                     _find_min_path_cover(root, leaves))
            root.children.add(child)
            leaves[id(root)] |= child_leaves
            return result


def find_min_path_cover(cotree: TreeNode[VT]) -> Set[Path[VT]]:
    def compute_leaves(cotree: TreeNode[VT]) -> Dict[int, Set[VT]]:
        if isinstance(cotree, LeafNode):
            return {id(cotree): singleton(cotree.node)}
        assert isinstance(cotree, InternalNode)

        def update_dicts(lhs: Dict[int, Set[VT]],
                         rhs: Dict[int, Set[VT]]) -> Dict[int, Set[VT]]:
            lhs.update(rhs)
            return lhs
        leaves = reduce(update_dicts, (compute_leaves(child)
                                       for child in cotree.children))
        leaves[id(cotree)] = set(flatten(leaves[id(child)]
                                         for child in cotree.children))
        return leaves

    leaves = compute_leaves(cotree)
    return _find_min_path_cover(cotree, leaves)

# pyright: strict
from __future__ import annotations
from typing import Iterable, TypeVar, Callable
import networkx as nx

Elem = TypeVar("Elem")


def pick(elements: Iterable[Elem]) -> Elem:
    for elem in elements:
        return elem


VertexOne = TypeVar("VertexOne")
VertexTwo = TypeVar("VertexTwo")
VO = VertexOne
VT = VertexTwo


def identity(thing: VertexOne) -> VertexOne:
    return thing


def is_homomorphism(
        graph_from: nx.Graph[VertexOne],
        graph_to: nx.Graph[VertexTwo],
        hom: Callable[[VertexOne], VertexTwo]) -> bool:
    return all(
        graph_to.has_edge(hom(node_u), hom(node_v))
        for (node_u, node_v) in graph_from.edges
    )


def are_isomorphic(
        graph_l: nx.Graph[VertexOne],
        graph_r: nx.Graph[VertexOne]) -> bool:
    return (is_homomorphism(graph_l, graph_r, identity) and
            is_homomorphism(graph_r, graph_l, identity))

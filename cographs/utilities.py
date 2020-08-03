# pyright: strict
from __future__ import annotations
from typing import Iterable, TypeVar, Callable, Set, Iterator, List
import networkx as nx

Elem = TypeVar("Elem")


def pick(elements: Iterable[Elem]) -> Elem:
    for elem in elements:
        return elem


def singleton(element: Elem) -> Set[Elem]:
    return set([element])


def sized_partition(elements: Set[Elem],
                    size: int) -> Iterator[List[Set[Elem]]]:
    assert len(elements) >= size
    if size == 0:
        return
    if len(elements) == size:
        yield [singleton(elem) for elem in elements]
        return

    first = elements.pop()
    for partition in sized_partition(elements, size):
        for part in partition:
            part.add(first)
            yield [part.copy() for part in partition]
            part.remove(first)
    elements.add(first)


def flatten(list_of_lists: Iterable[Iterable[Elem]]) -> Iterable[Elem]:
    return (elem for sublist in list_of_lists for elem in sublist)


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

# pyright: strict
from dataclasses import dataclass
from functools import reduce
from typing import Callable, TypeVar
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

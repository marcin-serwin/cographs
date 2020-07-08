from typing import Set, TypeVar

T = TypeVar('T')


def pickFromSet(s: Set[T]) -> T:
    for x in s:
        return x

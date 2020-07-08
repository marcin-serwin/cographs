from typing import Iterable, TypeVar

Elem = TypeVar('Elem')


def pick(elements: Iterable[Elem]) -> Elem:
    for elem in elements:
        return elem

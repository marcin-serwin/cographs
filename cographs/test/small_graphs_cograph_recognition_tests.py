from __future__ import annotations
from typing import Callable, Any, Tuple
import unittest
import os
import itertools
import networkx as nx
import timeout_decorator
import cographs.corneil_perl_stewart as cps
import cographs.habib_paul as hp

COGRAPHS_PATH = "resources/small-graphs/cographs/"
NOT_COGRAPHS_PATH = "resources/small-graphs/not-cographs/"


class SmallGraphsTests(unittest.TestCase):
    pass


def add_tests(cls,
              prefix: str,
              is_cograph: Callable[[nx.Graph], bool],
              full_path: Tuple[str, str],
              expected_value: bool):
    path, filename = full_path
    with open(path + filename) as batch:
        for line in batch:
            @timeout_decorator.timeout(.5)
            def test(self: SmallGraphsTests, line=line):
                graph: nx.Graph[Any] = nx.from_graph6_bytes(
                    bytes(line.strip(), "utf-8"))
                self.assertEqual(is_cograph(graph), expected_value)
            test.__name__ = "test_example_{}_{}_{}".format(
                prefix, os.path.splitext(filename)[0], line.strip())
            setattr(cls, test.__name__, test)


def clsinit():
    for (prefix, func), (path, expected_value) in itertools.product(
            [("cps", cps.is_cograph), ("hp", hp.is_cograph)],
            [(COGRAPHS_PATH, True), (NOT_COGRAPHS_PATH, False)]):
        for filename in os.listdir(path):
            add_tests(
                SmallGraphsTests,
                prefix,
                func,
                (path, filename),
                expected_value)


clsinit()


if __name__ == "__main__":
    unittest.main()

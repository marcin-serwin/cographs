from typing import Callable, Any
import unittest
import os
import itertools
import networkx as nx
import timeout_decorator
import cographs.corneil_perl_stewart as cps
import cographs.habib_paul as hp

COGRAPHS_PATH = "resources/example-graphs/cographs/"
NOT_COGRAPHS_PATH = "resources/example-graphs/not-cographs/"


class ExampleTests(unittest.TestCase):
    pass


def add_test(cls,
             prefix: str,
             is_cograph: Callable[[nx.Graph], bool],
             filename: str,
             expected_value: bool):
    @timeout_decorator.timeout(5)
    def test(self: ExampleTests):
        path = COGRAPHS_PATH if expected_value else NOT_COGRAPHS_PATH
        graph: nx.Graph[Any] = nx.read_yaml(path + filename)
        self.assertEqual(is_cograph(graph), expected_value)
    test.__name__ = "test_example_{}_{}".format(
        prefix, os.path.splitext(filename)[0])
    setattr(cls, test.__name__, test)


def clsinit():
    for (prefix, func), (graph_path, expected_value) in itertools.product(
            [("cps", cps.is_cograph), ("hp", hp.is_cograph)],
            [(COGRAPHS_PATH, True), (NOT_COGRAPHS_PATH, False)]):
        for path in os.listdir(graph_path):
            add_test(ExampleTests, prefix, func, path, expected_value)


# clsinit()


if __name__ == "__main__":
    unittest.main()

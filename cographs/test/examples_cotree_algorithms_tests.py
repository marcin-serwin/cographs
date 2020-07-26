from typing import Callable, Any, Tuple, TypeVar, cast
import unittest
import os
import networkx as nx
import timeout_decorator
import cographs.corneil_perl_stewart as cps
import cographs.verification_algorithms as ver
import cographs.cotree_algorithms as algos
from cographs.cotree_classes import TreeNode, VT

COGRAPHS_PATH = "resources/example-graphs/cographs/"
NOT_COGRAPHS_PATH = "resources/example-graphs/not-cographs/"


class ExamplesCotreeAlgorithmsTests(unittest.TestCase):
    pass


OT = TypeVar("OT")


def add_test(cls,
             prefix: str,
             algo: Callable[[TreeNode], OT],
             verify_algo_output: Callable[[nx.Graph, OT], bool],
             full_path: Tuple[str, str]):
    path, filename = full_path

    @timeout_decorator.timeout(5)
    def test(self: ExamplesCotreeAlgorithmsTests):
        graph: nx.Graph[Any] = nx.read_yaml(path + filename)
        cotree = cast(TreeNode[VT], cps.compute_cotree(graph))
        self.assertIsNotNone(cotree)
        self.assertTrue(verify_algo_output(graph, algo(cotree)))

    test.__name__ = "test_example_{}_{}".format(
        prefix, os.path.splitext(filename)[0])
    setattr(cls, test.__name__, test)


def clsinit():

    algorithms = [
        ("cliqe", ver.is_max_clique, algos.find_max_clique),
        ("iset", ver.is_max_independent_set, algos.find_max_independent_set),
        ("color", ver.is_optimal_coloring, algos.find_min_coloring),
        ("mpc", ver.is_min_path_cover, algos.find_min_path_cover)
    ]

    for filename in os.listdir(COGRAPHS_PATH):
        for prefix, verify, algo in algorithms:
            add_test(ExamplesCotreeAlgorithmsTests, prefix, algo, verify,
                     (COGRAPHS_PATH, filename))


clsinit()


if __name__ == "__main__":
    unittest.main()

import unittest
import os
import networkx as nx
import cographs.corneil_perl_stewart as cps

COGRAPHS_PATH = "resources/example-cographs/"
NOT_COGRAPHS_PATH = "resources/example-not-cographs/"


class ExampleCPSTest(unittest.TestCase):
    pass


def add_test(cls, filename, is_cograph):
    def test(self: ExampleCPSTest):
        path = COGRAPHS_PATH if is_cograph else NOT_COGRAPHS_PATH
        graph: nx.Graph[int] = nx.read_yaml(path + filename)
        assertion = self.assertIsNotNone if is_cograph else self.assertIsNone
        assertion(cps.compute_cotree(graph))
    test.__name__ = "test_example_{}".format(os.path.splitext(filename)[0])
    setattr(cls, test.__name__, test)


def clsinit():
    for path in os.listdir(COGRAPHS_PATH):
        add_test(ExampleCPSTest, path, True)

    for path in os.listdir(NOT_COGRAPHS_PATH):
        add_test(ExampleCPSTest, path, False)


clsinit()


if __name__ == "__main__":
    unittest.main()

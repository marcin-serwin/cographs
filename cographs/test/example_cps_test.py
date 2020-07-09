import unittest
import networkx as nx
import cographs.corneil_perl_stewart as cps

COGRAPHS_PATH = "resources/example-cographs/"
NOT_COGRAPHS_PATH = "resources/example-not-cographs/"


class ExampleCPSTest(unittest.TestCase):
    def test_habib_paul_example(self):
        graph: nx.Graph[int] = nx.read_yaml(
            COGRAPHS_PATH + "habib_paul_fig_1.yaml")
        self.assertIsNotNone(cps.compute_cotree(graph))

    def test_corneil_perl_stewart_example(self):
        graph: nx.Graph[int] = nx.read_yaml(
            COGRAPHS_PATH + "corneil_perl_stewart_fig_1.yaml")
        self.assertIsNotNone(cps.compute_cotree(graph))

    def test_dahlhaus_gustedt_mcconnel_example(self):
        graph: nx.Graph[int] = nx.read_yaml(
            NOT_COGRAPHS_PATH + "dahlhaus_gustedt_mcconnel_fig_1.yaml")
        self.assertIsNone(cps.compute_cotree(graph))


if __name__ == "__main__":
    unittest.main()

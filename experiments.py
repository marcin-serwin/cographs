from typing import Callable
import timeit
import random
import networkx as nx
import cographs.corneil_perl_stewart as cps
import cographs.habib_paul as hp
import cographs.cotree_algorithms as ca
import cographs.verification_algorithms as va

SAMPLE_SIZE = 100


def get_cograph(logsize: int, seed: int) -> nx.Graph:
    return nx.generators.cographs.random_cograph(logsize, seed)


def get_graph(logsize: int, seed: int) -> nx.Graph:
    random.seed(seed)
    n = 2**logsize
    m = random.randint(0, n * (n - 1) / 2)
    return nx.generators.random_graphs.gnm_random_graph(n, m, seed)


NOT_COGRAPHS = {(logsize, seed): get_graph(logsize, seed)
                for logsize in [4, 8, 10] for seed in range(SAMPLE_SIZE)}

COGRAPHS = {(logsize, seed): get_cograph(logsize, seed)
            for logsize in [2, 3, 4, 8, 10] for seed in range(SAMPLE_SIZE)}


def test_recognition_algo(algo: Callable, name: str, positive_answer: bool):

    print(name, "positive" if positive_answer else "negative")
    graph_generator = COGRAPHS if positive_answer else NOT_COGRAPHS
    for log_graph_order in [4, 8, 10]:
        deltas = [
            1000 * timeit.timeit(
                lambda: algo(graph_generator[(log_graph_order, seed)]),
                number=1)
            for seed in range(SAMPLE_SIZE)]
        print(
            2**log_graph_order,
            "{:.4f}".format(sum(deltas) / SAMPLE_SIZE),
            "{:.4f}".format(max(deltas)))


def test_cotree_algo(algo: Callable, brute: Callable, name: str):
    print(name)

    for log_graph_order in [2, 3, 4, 8, 10]:
        deltas = [
            1000 *
            timeit.timeit(
                lambda: algo(cps.compute_cotree(
                    COGRAPHS[(log_graph_order, seed)])),
                number=1) for seed in range(SAMPLE_SIZE)]
        print(
            2**log_graph_order,
            "{:.4f}".format(sum(deltas) / SAMPLE_SIZE),
            "{:.4f}".format(max(deltas)))

    print("brute", name)

    for log_graph_order in [2, 3]:
        deltas = [
            1000 *
            timeit.timeit(
                lambda: brute(
                    COGRAPHS[(log_graph_order, seed)]),
                number=1) for seed in range(SAMPLE_SIZE)]
        print(
            2**log_graph_order,
            "{:.4f}".format(sum(deltas) / SAMPLE_SIZE),
            "{:.4f}".format(max(deltas)))


def verificator_to_bruteforce(algo: Callable, top_down: bool) -> Callable:
    def bruteforce(graph: nx.Graph):
        for i in range(graph.number_of_nodes())[::-1 if top_down else 1]:
            if algo(graph, i):
                break

    return bruteforce


def main():
    ALGORITHMS = [
        (lambda g: hp.check_partition(
            g,
            hp.brute_force_partition(g)), "brute"),
        (hp.is_cograph, "hp"),
        (cps.is_cograph, "cps")]

    for algo, name in ALGORITHMS:
        test_recognition_algo(algo, name, True)

    for algo, name in ALGORITHMS:
        test_recognition_algo(algo, name, False)

    COTREE_ALGORITHMS = [
        ("cliq",
         ca.find_max_clique,
         verificator_to_bruteforce(va.clique_of_size_exists, True)),
        ("is",
         ca.find_max_independent_set,
         verificator_to_bruteforce(va.independent_set_of_size_exists, True)),
        ("color",
         ca.find_min_coloring,
         verificator_to_bruteforce(va.is_graph_colorable_with, False)),
        ("paths",
         ca.find_min_path_cover,
         verificator_to_bruteforce(va.can_be_covered_with, False)),
    ]

    for name, algo, brute in COTREE_ALGORITHMS:
        test_cotree_algo(algo, brute, name)


if __name__ == "__main__":
    main()

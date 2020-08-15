from typing import Callable
import timeit
import random
import networkx as nx
import cographs.corneil_perl_stewart as cps
import cographs.habib_paul as hp

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
            for logsize in [4, 8, 10] for seed in range(SAMPLE_SIZE)}


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


if __name__ == "__main__":
    main()

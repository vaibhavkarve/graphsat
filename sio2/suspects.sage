#!/usr/bin/env sage
"""Using SageMath's wrapper for Nauty to generate 3sat cases.

Note:
   Run this file from inside Sage.

Look at the following link for nauty's documentation:
   http://doc.sagemath.org/html/en/reference/graphs/sage/graphs/hypergraph_generators.html
"""
# pylint: disable=invalid-name, import-error, wrong-import-order
import itertools as it
import multiprocessing as mp
from typing import Iterator, List, Tuple
from sage.graphs.hypergraph_generators import HypergraphGenerators as HG

from loguru import logger
import typer

import config

Vertex = int
HEdge = Tuple[int, ...]
HGraph = Tuple[HEdge, ...]


def process_nauty_output(hypergraphs: Iterator[HGraph]) -> List[str]:
    """Process hypergraphs."""
    logger.info(f'Parallelizing renumber_vertices() accross {mp.cpu_count()} cores.')
    with mp.Pool(8) as p:
        return p.map(renumber_vertices, hypergraphs)


def renumber_vertices(hgraph: HGraph) -> str:
    """Given an HGraph, renumber its vertices to start from 1 instead of zero.

    Reorder the hedges (borrowed from the canonical ordering in
    graphsat's ``mhgraph.PreMHGraph.__repr__``)

    """
    new_hgraph: List[List[int]]
    new_hgraph = [[vertex+1 for vertex in hedge] for hedge in hgraph]

    ordered_hedges: List[List[int]]
    ordered_hedges = sorted(sorted([sorted(hedge) for hedge in new_hgraph]), key=len)

    return str(ordered_hedges)


def call_nauty(v: int, emin: int, emax: int, mixed: str, multi: str) \
        -> Iterator[Iterator[HGraph]]:
    for E in range(emin, emax):
        yield HG().nauty(number_of_sets=E,
                         number_of_vertices=v,
                         multiple_sets=multi == 'Multi',
                         vertex_min_degree=2,
                         vertex_max_degree=None,
                         set_max_size=3,
                         set_min_size=2 if mixed == 'Mixed' else 3,
                         regular=False,
                         uniform=False,
                         max_intersection=None,
                         connected=True,
                         debug=False,
                         options='')


def generate_hgraphs(cli_args: config.ArgsType) -> List[str]:
    """For a fixed number of vertices v, generate all the HGraphs.

    Conditions passed to Nauty
       * The number of HEdges will range between emin and emax.
       * These HGraphs will have no multiplicities (unless Multi is True).
       * Isolated vertices not allowed (enforced by min_degree >= 2).
       * Pendant (H)Edges not allowed (enforced by min_degree >= 2).
         [This and the previous rule account for the (H)Edge-popping pattern.]
       * Hedges must have size 3 or 2 (if mixed).
       * HGraphs should be connected.

    """
    hypergraph_iters: Iterator[Iterator[HGraph]]
    hypergraph_iters = call_nauty(*cli_args)
    hypergraphs = it.chain.from_iterable(hypergraph_iters)
    return process_nauty_output(hypergraphs)


def write_suspects(v: int = config.ARGDOCS['v'],
                   emin: int = config.ARGDOCS['emin'],
                   emax: int = config.ARGDOCS['emax'],
                   mixed: str = config.ARGDOCS['mixed'],
                   multi: str = config.ARGDOCS['multi']) -> None:
    """Generate hypergraphs and write to suspects.dat in correct folder."""
    cli_args: config.ArgsType = (v, emin, emax, mixed, multi)
    hypergraph_str: List[str] = generate_hgraphs(cli_args)

    with open(config.files('suspects', cli_args), 'w') as writefile:
        writefile.write('\n'.join(iter(hypergraph_str)) + '\n')
    config.print_end_message()


if __name__ == '__main__':
    from time import time
    time0 = time()
    typer.run(write_suspects)

#!/usr/bin/env python3.9
"""Given a MHGraph, this module constructs highly hyperbolic Cnf that's likely
to be unsatisfiable.

The hyperbolic Cnf is constructed by assigning ⌊n/2⌋ clauses at a vertex to one
sign and the remaining to the other sign.

TODO: Some loops in this file can be parallelized using multiprocessing.Pool.

"""
from collections import Counter as counter
import multiprocessing as mp
from typing import Counter, Iterator

from tqdm import tqdm

import cnf
import graph
import mhgraph as mhg
import sat



def hyperbolic_filter(vertices: frozenset[graph.Vertex], cnf_: cnf.Cnf) -> bool:
    """Return True only if the Cnf is maximally hyperbolic at each vertex."""
    for vertex in vertices:
        if abs(sum([lit for clause in cnf_ for lit in clause if lit in {vertex, -vertex}])) > vertex:
            return False
    return True


def generate_hyperbolic_cnfs(mhgraph: mhg.MHGraph) -> Iterator[cnf.Cnf]:
    """Return all Cnfs that are maximally hyperbolic.

    We claim that every unsatisfiable Cnf on a (minimal) MHGraph must be
    maximally hyperbolic.

    We do not however claim that every maximally hyperbolic Cnf is
    unsatisfiable.
    """
    vertices: frozenset[graph.Vertex] = mhg.vertices(mhgraph)
    return filter(lambda cnf_: hyperbolic_filter(vertices, cnf_),
                  sat.cnfs_from_mhgraph(mhgraph))


def mhgraph_hyperbolic_satcheck(mhgraph: mhg.MHGraph) -> bool:
    """Return True if all hyperbolic Cnfs on the mhgraph are satisfiable.

    Currently this function is slower than sat.mhgraph_pysat_satcheck.
    """
    return  all(map(sat.cnf_pysat_satcheck, generate_hyperbolic_cnfs(mhgraph)))


if __name__ == '__main__':
    mhgraph_: mhg.MHGraph = mhg.mhgraph([[1, 2, 3],
                                         [4, 1, 2], [4, 1, 3], [4, 2, 3],
                                         [5, 1, 2], [5, 1, 3], [5, 2, 3]])
    print(f'{mhgraph_ = }')
    print(mhgraph_hyperbolic_satcheck(mhgraph_))

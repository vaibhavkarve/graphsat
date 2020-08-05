#!/usr/bin/env python3.8
"""Functions and operations."""
# Imports from standard library.
import functools as ft
from typing import Union
# Imports from third-party modules.
from loguru import logger
# Imports feom local modules.
from graphsat import mhgraph, sat, sxpr

from graphsat.mhgraph import MHGraph
from graphsat.sxpr import SatSxpr


@ft.singledispatch
def satg(arg: Union[bool, MHGraph, SatSxpr]) -> bool:  # type: ignore
    """Sat-solve if it is a graph. Else just return the bool."""
    print(type(arg))
    raise TypeError


@satg.register
def satg_bool(boolean: bool) -> bool:
    """Return the boolean."""
    return boolean


@satg.register
def satg_graph(graph: MHGraph) -> bool:
    """Sat-solve."""
    return sat.mhgraph_pysat_satcheck(graph)


@satg.register
def satg_sxpr(sat_sxpr: SatSxpr) -> bool:  # type: ignore
    """Reduce and then sat-solve."""
    return satg(sat_sxpr.reduce())


def sat_and(graph1: Union[bool, MHGraph, AtomicSxpr],
            graph2: Union[bool, MHGraph, AtomicSxpr]) -> bool:
    """Return the conjunction of the sat-status of each graph."""
    return satg(graph1) and satg(graph2)


def sat_or(graph1: Union[bool, MHGraph, AtomicSxpr],
           graph2: Union[bool, MHGraph, AtomicSxpr]) -> bool:
    """Return the disjunction of the sat-status of each graph."""
    return satg(graph1) or satg(graph2)


def gor(graph1: Union[MHGraph, Set[cnf.CNF]],
        graph2: Union[MHGraph, Set[cnf.CNF]]) -> Set[cnf.CNF]:
    """Disjunct the corresponding CNFs."""
    if not isinstance(graph1, set):
        graph1 = set(sat.cnfs_from_mhgraph(mhgraph(graph1)))
    if not isinstance(graph2, set):
        graph2 = set(sat.cnfs_from_mhgraph(mhgraph(graph2)))

    product = it.product(graph1, graph2)
    disjunction = it.starmap(prop.cnf_or_cnf, product)
    disjunction_reduced = map(cnf.tautologically_reduce_cnf, disjunction)
    return set(disjunction_reduced)


def gand(graph1: Union[MHGraph, Set[cnf.CNF]],
        graph2: Union[MHGraph, Set[cnf.CNF]]) -> Set[cnf.CNF]:
    """Conjunct the corresponding CNFs."""
    if not isinstance(graph1, set):
        graph1 = set(sat.cnfs_from_mhgraph(mhgraph(graph1)))
    if not isinstance(graph2, set):
        graph2 = set(sat.cnfs_from_mhgraph(mhgraph(graph2)))

    product = it.product(graph1, graph2)
    conjunction = it.starmap(prop.cnf_and_cnf, product)
    conjunction_reduced = map(cnf.tautologically_reduce_cnf, conjunction)
    return set(conjunction_reduced)

if __name__ == "__main__":
    from time import time
    with logger.catch(message="Something unexpected happened ..."):
        time0 = time()

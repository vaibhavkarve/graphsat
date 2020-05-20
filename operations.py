#!/usr/bin/env python3.8
"""Functions and operations."""
# Imports from standard library.
import functools as ft
from typing import List, Union
# Imports from third-party modules.
from loguru import logger
# Imports feom local modules.
import mhgraph
import sat
import sxpr


def graph_union(graph1: List[mhgraph.HEdge], graph2: List[mhgraph.HEdge]) -> mhgraph.MHGraph:
    """Union of the two graphs."""
    return mhgraph.mhgraph(graph1 + graph2)


@ft.singledispatch
def satg(arg: Union[bool, mhgraph.MHGraph, sxpr.AtomicSxpr]) -> bool:
    """Sat-solve if it is a graph. Else just return the bool."""
    raise TypeError


@satg.register
def satg_bool(boolean: bool) -> bool:
    """Return the boolean."""
    return boolean


@satg.register(mhgraph.MHGraph)
def satg_graph(graph: mhgraph.MHGraph) -> bool:
    """Sat-solve."""
    return sat.mhgraph_pysat_satcheck(graph)


@satg.register(sxpr.SatSxpr)
def satg_sxpr(atomic: sxpr.AtomicSxpr) -> bool:
    """Reduce and then sat-solve."""
    return satg(atomic.reduce())


def sat_and(graph1: Union[bool, mhgraph.MHGraph, sxpr.AtomicSxpr],
            graph2: Union[bool, mhgraph.MHGraph, sxpr.AtomicSxpr]) -> bool:
    """Return the conjunction of the sat-status of each graph."""
    return satg(graph1) and satg(graph2)


def sat_or(graph1: Union[bool, mhgraph.MHGraph, sxpr.AtomicSxpr],
           graph2: Union[bool, mhgraph.MHGraph, sxpr.AtomicSxpr]) -> bool:
    """Return the disjunction of the sat-status of each graph."""
    return satg(graph1) or satg(graph2)


if __name__ == "__main__":
    from time import time
    with logger.catch(message="Something unexpected happened ..."):
        time0 = time()

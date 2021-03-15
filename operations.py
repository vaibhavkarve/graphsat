#!/usr/bin/env python3.9
"""Functions and operations for working with Graph-Satisfiability."""

# Imports from standard library.
import functools as ft
import itertools as it
from typing import Union

# Imports from third-party modules.
from loguru import logger

# Imports from local modules.
import cnf
import prop
import sat
from mhgraph import MHGraph, mhgraph
from sxpr import AtomicSxpr, SatSxpr


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


def graph_or(graph1: Union[MHGraph, set[cnf.Cnf]],
             graph2: Union[MHGraph, set[cnf.Cnf]]) -> set[cnf.Cnf]:
    """Disjunct the corresponding Cnfs."""
    if not isinstance(graph1, set):
        graph1 = set(sat.cnfs_from_mhgraph(mhgraph(graph1)))
    if not isinstance(graph2, set):
        graph2 = set(sat.cnfs_from_mhgraph(mhgraph(graph2)))

    product = it.product(graph1, graph2)
    disjunction = it.starmap(prop.cnf_or_cnf, product)
    disjunction_reduced = map(cnf.tautologically_reduce_cnf, disjunction)
    return set(disjunction_reduced)


def graph_and(graph1: Union[MHGraph, set[cnf.Cnf]],
              graph2: Union[MHGraph, set[cnf.Cnf]]) -> set[cnf.Cnf]:
    """Conjunct the corresponding Cnfs."""
    if not isinstance(graph1, set):
        graph1 = set(sat.cnfs_from_mhgraph(mhgraph(graph1)))
    if not isinstance(graph2, set):
        graph2 = set(sat.cnfs_from_mhgraph(mhgraph(graph2)))

    product = it.product(graph1, graph2)
    conjunction = it.starmap(prop.cnf_and_cnf, product)
    conjunction_reduced = map(cnf.tautologically_reduce_cnf, conjunction)
    return set(conjunction_reduced)


def graphs_equisat_a_bot(graph1: set[cnf.Cnf], graph2: set[cnf.Cnf]) -> bool:
    """Check ∀ x₁ ∈ G₁, ∃ x₂ ∈ G₂, ∀ a ∈ A, x₁[a] ~ ⊥ → x₂[a] ~ ⊥."""
    particular_x1: cnf.Cnf = graph1.pop()
    graph1.add(particular_x1)  # add it back in.

    assignments: list[sat.Assignment]
    assignments = list(sat.generate_assignments(particular_x1))

    def cnf1_falsified(cnf1: cnf.Cnf, assignment: sat.Assignment) -> bool:
        cnf1_assigned: cnf.Cnf = cnf.assign(cnf1, assignment)
        assert all(map(lambda l: isinstance(l, cnf.Bool), cnf.lits(cnf1_assigned)))
        return not sat.cnf_pysat_satcheck(cnf1_assigned)

    def cnf2_falsified(cnf2: cnf.Cnf, assignment: sat.Assignment) -> bool:
        return not sat.cnf_pysat_satcheck(cnf.assign(cnf2, assignment))

    return all(any(all(cnf2_falsified(cnf2, a)
                       for a in assignments if cnf1_falsified(cnf1, a))
                   for cnf2 in graph2) for cnf1 in graph1)


def graph_equisat_mod_sphr(graph1: Union[MHGraph, set[cnf.Cnf]],
                           graph2: Union[MHGraph, set[cnf.Cnf]]) -> bool:
    """Check graphs are quisat by the A⊥ criterion.

    This helps us conclude that Sphr∧G₁ is equisat to Sphr∧G₂ by the ⊥
    criterion.
    """
    if not isinstance(graph1, set):
        graph1 = set(sat.cnfs_from_mhgraph(mhgraph(graph1)))
    if not isinstance(graph2, set):
        graph2 = set(sat.cnfs_from_mhgraph(mhgraph(graph2)))

    assert graph1 and graph2
    return graphs_equisat_a_bot(graph1, graph2) \
        and graphs_equisat_a_bot(graph1=graph2, graph2=graph1)


if __name__ == "__main__":
    from time import time
    with logger.catch(message="Something unexpected happened ..."):
        time0 = time()


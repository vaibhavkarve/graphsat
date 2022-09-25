#!/usr/bin/env python3
"""Functions for sat-checking Graphs, and MHGraphs; and translating between Cnfs and MHGraphs.


Connection between Cnfs and MHGraphs
====================================
For every Cnf, we can construct an associated MHGraph by replacing all variables and
their negations by vertices of the same name.

Satisfiability of a MHGraph
===========================
A MHGraph is satisfiable if it has atleast one Cnf supported on it and every Cnf
supported on the MHGraph is also satisfiable.  This module implements three different
MHGraph sat-solvers:

    1. mhgraph_bruteforce_satcheck: easiest to understand and reason about.
    2. mhgraph_pysat_satcheck: faster.
    3. mhgraph_minisat_satcheck: slowest.

"""
import math
import itertools as it
from typing import Iterator, cast
import more_itertools as mit
from loguru import logger
from normal_form.sat import cnf_bruteforce_satcheck, cnf_minisat_satcheck, cnf_pysat_satcheck
from graphsat import graph, morphism as morph
from graphsat.mhgraph import HEdge, MHGraph, degree, graph_union, link, mhgraph, pick_min_degree_vertex, sphr, vertices
from normal_form.cnf import FALSE_CNF, TRUE_CNF, Bool, Lit, absolute_value, lit, neg, Clause, clause, Cnf, cnf, tauto_reduce
from tqdm import tqdm

# Functions for generating Cnfs from MHGraphs
# ===========================================


def lits_from_vertex(vertex: graph.Vertex) -> tuple[Lit, Lit]:
    """Return a Lit as well as its negation from a Vertex.

    Args:
       vertex (:obj:`graph.Vertex`)

    Returns:
       ``vertex`` and ``neg(vertex)`` after casting each to Lit.

    """
    positive_lit: Lit = lit(vertex)
    return positive_lit, neg(positive_lit)


def clauses_from_hedge(hedge: HEdge) -> tuple[Clause, ...]:
    r"""Return all Clauses supported on a HEdge.

    Args:
       hedge (:obj:`HEdge`)

    Return:
       An iterator of Clause consisting of the :math:`2^{|\texttt{hedge}|}` Clauses
       that are supported on ``hedge``.

    """
    lits_positive_and_negative: Iterator[tuple[Lit, Lit]]
    lits_positive_and_negative = map(lits_from_vertex, hedge)

    lit_combinations: Iterator[tuple[Lit, ...]]
    lit_combinations = it.product(*lits_positive_and_negative)

    return tuple(map(clause, lit_combinations))


def cnfs_from_hedge(hedge: HEdge, multiplicity: int) -> Iterator[Cnf]:
    r"""Return all Cnfs supported on a HEdge with multiplicity.

    Args:
       hedge (:obj:`HEdge`)
       multiplicity (:obj:`int`): an integer in the range
          :math:`\{1, \ldots, 2^{|hedge|}\}`.

    Returns:
       An iterator of Cnf consisting of the :math:`\binom{2^{|hedge|}}{multiplicity}`
       Cnfs supported on a HEdge ``hedge`` with multiplicity ``multiplicity``.

    Edge case:
       Returns an empty iterator if ``multiplicity`` greater than :math:`2^{|hedge|}`.

    Raises:
       ValueError if ``multiplicity`` is less than 1.

    """
    clause_possibilities: tuple[Clause, ...]
    clause_possibilities = clauses_from_hedge(hedge)

    clause_tuples: Iterator[tuple[Clause, ...]]
    clause_tuples = it.combinations(clause_possibilities, r=multiplicity)

    return map(cnf, clause_tuples)


def cnfs_from_mhgraph(mhgraph_instance: MHGraph,
                      randomize: bool = True) -> Iterator[Cnf]:
    r"""Return all Cnfs supported on a MHGraph.

    Args:
       mhgraph_instance (:obj:`MHGraph`)
       randomize (:obj:`bool`): if True (default) then return all cnfs in a
          shuffled order.

    Returns:
       An iterator of Cnf consisting of the
       :math:`\displaystyle\prod_{hedge}\binom{2^{|hedge|}}{multiplicity}` Cnfs supported
       on the MHGraph ``mhgraph_instance``.

    Edge case:
       If `mhgraph_instance` is over-saturated (i.e. if it has a HEdge with multiplicity
       greater than :math:`2^{|hedge|}`, then this function returns an empty iterator.
    """
    cnf_iterators: Iterator[Iterator[Cnf]]
    cnf_iterators = it.starmap(cnfs_from_hedge, mhgraph_instance.items())

    # Iterator[tuple[Cnf, ...]] <: Iterator[tuple[frozenset[Clause], ...]]
    cnf_tuples: Iterator[tuple[Cnf, ...]]
    cnf_tuples = it.product(*cnf_iterators)

    clause_frozensets: Iterator[frozenset[Clause]]
    clause_frozensets = it.starmap(frozenset.union, cnf_tuples)

    if not randomize:
        return map(cnf, clause_frozensets)

    return map(cnf, mit.random_permutation(clause_frozensets))


def number_of_cnfs(mhgraph_instance: MHGraph) -> int:
    """Return the number of Cnfs supported on a MHGraph.

    Returns `0` in case of over-saturated graphs.
    """
    return math.prod(math.comb(2**len(h), m)
                     for h, m in mhgraph_instance.items())


# Function for generating MHGraphs from Cnfs
# ==========================================


def mhgraph_from_cnf(cnf_instance: Cnf) -> MHGraph:
    """Return the MHGraph that supports a given Cnf.

    This function first tautologically reduces the Cnf using :obj:`tauto_reduce()`.
    This ensures no self-loops or collapsed HEdges in the final MHGraph.

    Args:
       cnf_instance (:obj:`Cnf`): a Cnf that does not tautologically reduce to
          ``cnf([[Bool.TRUE]])`` or ``cnf([[Bool.FALSE]])``.

    Return:
       The MHGraph that supports ``cnf_instance``.

    Raises:
       ValueError: If ``cnf_instance`` is trivially `True` or trivially `False`
          after performing tautological reductions.

    """
    reduced_cnf: Cnf = tauto_reduce(cnf_instance)

    if reduced_cnf in {TRUE_CNF, FALSE_CNF}:
        raise ValueError('Cnf reduced to trivial True/False & has no supporting MHGraph.')

    # Iterator[frozenset[Lit]] <: Iterator[Collection[int]]
    cnf_with_abs_variables: list[frozenset[int | Bool]]
    cnf_with_abs_variables = [
        frozenset({absolute_value(literal).value for literal in clause_instance})
        for clause_instance in reduced_cnf]  # pylint: disable=not-an-iterable
    for fset in cnf_with_abs_variables:
        assert all(isinstance(value, int) for value in fset)

    return mhgraph(cast(list[frozenset[int]], cnf_with_abs_variables))


# Function for simplifying MHGraphs before sat-solving
# ====================================================


def is_oversaturated(mhg: MHGraph) -> bool:
    """Return True if any edge of mhg of size n has multiplicity more than 2^n."""
    return any(mult > 2**len(hedge) for hedge, mult in mhg.items())


def simplify_at_leaves(mhg: MHGraph) -> bool | MHGraph:
    """If the graph contains a degree-one vertex, then remove that HEdge.

    This results in a graph that is equisatisfiable to the first.

    Edge cases:

       * if every HEdges is a leaf edge, then return True.

       * In the limit, the resulting mhgraph is guaranteed to have all vertices be
         degree >= 2.

    """
    leaf_vertex: graph.Vertex = pick_min_degree_vertex(mhg)
    if degree(leaf_vertex, mhg) > 1:
        return mhg
    sphr_: tuple[HEdge, ...] = sphr(mhg, leaf_vertex)
    if not sphr_:
        return True
    return mhgraph(sphr_)


def has_double_loop(mhg: MHGraph) -> bool:
    """Return True iff mhg has a double loop."""
    double_loop_graph: MHGraph
    double_loop_graph = mhgraph([[37], [37]])

    return morph.subgraph_search(double_loop_graph, mhg, return_all=False)[0]


def supports_single_loop(mhg: MHGraph) -> bool | graph.Vertex:
    """Return a vertex that supports a loop in mhg.

    If no such vertex exists, return False.

    """
    loops: list[graph.Vertex]
    loops = [vertex for vertex in vertices(mhg) if frozenset([vertex]) in mhg]
    logger.trace(f'{loops = }')
    return loops[0] if loops else False

import functools as ft
@ft.cache
def simplify_at_loops(mhg: MHGraph) -> bool | MHGraph:
    """If the graph contains a self loop, then project away from vertex.

    This results in a graph that is equisatisfiable to the first.
    """
    if has_double_loop(mhg):
        logger.trace(f'{mhg} simplified to False because of double loop.')
        return False

    vertex = supports_single_loop(mhg)
    if not vertex:
        logger.trace(f'{mhg} has no loops')
        return mhg

    vertex = cast(graph.Vertex, vertex)
    logger.trace(f'{vertex = }')

    sphr_: tuple[HEdge, ...] = sphr(mhg, vertex)

    link_: tuple[HEdge, ...] = link(mhg, vertex)

    if not link_ and not sphr_:
        # iff mhg is isomorphic to a bunch of loops at the verrtex.  But since we
        # already ruled out double loops (or higher), we can be sure that mhg has
        # only one loop.
        assert len(list(mhg.elements())) == 1
        logger.trace(f'{mhg} simplified to True')
        return True

    sphr_link: MHGraph = graph_union(sphr_, link_)
    logger.info(f'{mhg} simplified to {sphr_link}')
    return sphr_link

@logger.catch
def simplify_at_leaves_and_loops(mhg: MHGraph) -> bool | MHGraph:
    """Call both simplify_at_leaves() and simplify_at_loops().

    This resultant graph is always equisatisfiable to the input graph.

    """
    mhg_simp: bool | MHGraph
    match (mhg_simp := simplify_at_leaves(mhg)):
        case bool():
            # Reached bool. No further simplification possible.
            return mhg_simp
        case MHGraph() if mhg_simp != mhg:
            # Recusrive call.
            return simplify_at_leaves_and_loops(mhg_simp)
        case MHGraph():
            # Leaf simplification done. Try loop simplification.
            match (mhg_simp := simplify_at_loops(mhg)):
                case bool():
                    # Reached bool. No further simplification possible.
                    return mhg_simp
                case MHGraph() if mhg_simp != mhg:
                    # Recursive call.
                    return simplify_at_leaves_and_loops(mhg_simp)
                case MHGraph():
                    # Fixed point reached.
                    return mhg_simp
    assert False, "unreachable"

# Functions for Checking Satisfiability of MHGraphs
# =================================================


def mhgraph_bruteforce_satcheck(mhgraph_instance: MHGraph,
                                randomize: bool = True) -> bool:
    """Use brute-force to check satisfiability of a MHGraph.

    .. note::
       Brute-forcing is the most sub-optimal strategy
       possible. Do not use this function on large MHGraphs. (Anything
       more than 6 Vertices or 6 HEdges is large.)

    Args:
       mhgraph_instance (:obj:`MHGraph`)
       randomize (:obj:`bool`): if True (default) then generate all cnfs in
          a shuffled order.

    Return:
       ``True`` if ``mhgraph_instance`` is satisfiable, else return ``False``.

    """
    if number_of_cnfs(mhgraph_instance):
        return all(map(cnf_bruteforce_satcheck,
                       cnfs_from_mhgraph(mhgraph_instance, randomize=randomize)))
    return False


@ft.cache
def mhgraph_pysat_satcheck(mhgraph_instance: MHGraph, randomize: bool = True) -> bool:
    """Use the `pysat` library's Minisat22 solver to check satisfiability of a MHGraph.

    Args:
       mhgraph_instance (:obj:`MHGraph`)
       randomize (:obj:`bool`): if True (default) then generate all cnfs in a shuffled order.

    Return:
       ``True`` if ``mhgraph_instance`` is satisfiable, else return ``False``.

    Edge case:
       * If ``mhgraph_instance`` is over-saturated, then the number of cnfs on it is zero,
         and this function immediately returns False.
    """
    number: int = number_of_cnfs(mhgraph_instance)
    progress_bar = tqdm(cnfs_from_mhgraph(mhgraph_instance, randomize=randomize),
                        desc='pysat()',
                        total=number,
                        leave=False)
    return all(cnf_pysat_satcheck(cnf) for cnf in progress_bar) if number else False


def mhgraph_minisat_satcheck(mhgraph_instance: MHGraph) -> bool:
    """Use the `subprocess` library to launch `minisat.c` and sat-check a MHGraph.

    Args:
       mhgraph_instance (:obj:`MHGraph`)

    Return:
       ``True`` if ``mhgraph_instance`` is satisfiable, else return ``False``.

    """
    if number_of_cnfs(mhgraph_instance):
        return all(map(cnf_minisat_satcheck, cnfs_from_mhgraph(mhgraph_instance)))
    return False


if __name__ == '__main__':  # pragma: no cover
    logger.info('mhgraph_pysat_satcheck() finds all Cnfs supported on a MHGraph\n'
                + ' '*61 + 'and then sat-checks them using the pysat satchecker.')
    logger.info('>>> mhgraph_pysat_satcheck()(mhgraph([[1, 2], [2, 3]]))')
    logger.success(mhgraph_pysat_satcheck(mhgraph([[1, 2], [2, 3]])))
    logger.info('True output indicates that this MHGraph only supports satisfiable Cnfs.')
    logger.info('\n')
    logger.info('Given a Cnf we can also ask for its supporting MHGraph.')
    logger.info('>>> mhgraph_from_cnf(cnf([[1, -2], [2, 3, 4], [1, 2]]))')
    logger.success(mhgraph_from_cnf(cnf([[1, -2], [2, 3, 4], [1, 2]])))

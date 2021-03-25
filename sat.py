#!/usr/bin/env python3.9
"""Functions for sat-checking Cnfs, Graphs, and MHGraphs.

Satisfiability of Cnfs
======================
A Cnf is satisfiable if there exists a truth assignment for each variable in the Cnf
such that on applying the assignment, the Cnf evaluates to True.
This module implements three different sat-solvers:

   1. cnf_bruteforce_satcheck: a brute-force solver.  This solver is easy to
      understand and reason about. It does not have other external
      dependencies. However, it is quite slow.

   2. cnf_pysat_satcheck: using the `pysat` library's Minisat22 solver.  This solver
      calls Minisat v2.2 via the pysat library. It is the fast solver in this list
      but has many external dependencies (because pysat has many dependencies).

   3. cnf_minisat_satcheck: using Minisat v2.2 as a subprocess.  This calls minisat.c
      directly as a subprocess. minisat.c is easy to obtain and install. However,
      creating subprocesses is not a very fast process.

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

TODO: Add a function for equisatisfiability of Cnfs
"""
# Imports from standard library
import functools as ft
import itertools as it
import math
import subprocess
from typing import cast, Iterator, Union
# Imports from third-party modules.
from loguru import logger
import more_itertools as mit  # type: ignore
from tqdm import tqdm  # type: ignore
# Imports from local modules.
import cnf
import graph
import mhgraph
import morphism as morph


# Type alisases
Assignment = dict[cnf.Variable, cnf.Bool]


# Functions for Checking Satisfiability of Cnfs
# =============================================


def generate_assignments(cnf_instance: cnf.Cnf) -> Iterator[Assignment]:
    """Generate all :math:`2^n` truth-assignments for a Cnf with :math:`n` Variables.

    A Cnf's `truth-assignment` will be represented as a dictionary with keys being
    all the Variables that appear in the Cnf and values being Bools.

    Edge cases:

       * ``TRUE``/``FALSE`` Cnfs are treated as having :math:`0` Variables and
         therefore their only corresponding truth-assignment is the empty dictionary.
         In other words, the function returns ``({})``.

       * Any Cnf that can be tautologically reduced to TRUE/FALSE also returns ``({})``.

       * This function cannot distinguish between sat/unsat Cnfs.

    Args:
       cnf_instance (:obj:`cnf.Cnf`)

    Return:
       First, tautologically reduce the Cnf. Then, return an Iterator of
       truth-assignment dictionaries with keys being Variables and values being
       Bools.

    """
    cnf_reduced: cnf.Cnf
    cnf_reduced = cnf.tautologically_reduce_cnf(cnf_instance)

    lit_set: frozenset[cnf.Lit]
    lit_set = cnf.lits(cnf_reduced) - {cnf.TRUE, cnf.FALSE}

    variable_set: set[cnf.Variable]
    variable_set = set(map(cnf.variable, map(cnf.absolute_value, lit_set)))

    assignment_values: Iterator[tuple[cnf.Bool, ...]]
    assignment_values = it.product([cnf.TRUE, cnf.FALSE], repeat=len(variable_set))

    for boolean_tuple in assignment_values:
        yield dict(zip(variable_set, boolean_tuple))


def cnf_bruteforce_satcheck(cnf_instance: cnf.Cnf) -> bool:
    """Use brute force to check satisfiability of Cnf.

    .. note::
       Brute-forcing is the most sub-optimal strategy possible. Do not use this function
       on large Cnfs. (Anything more than 6 Variables or 6 Clauses is large.)

    Args:
       cnf_instance (:obj:`cnf.Cnf`)

    Return:
       First, tautologically reduce the Cnf. Then. if the Cnf is Satisfiable return
       ``True`` else return ``False``.

    """
    cnf_reduced: cnf.Cnf
    cnf_reduced = cnf.tautologically_reduce_cnf(cnf_instance)

    if cnf_reduced == cnf._TRUE_CNF:
        return True
    if cnf_reduced == cnf._FALSE_CNF:
        return False

    def assigns_cnf_to_true(assignment: Assignment) -> bool:
        return cnf.assign(cnf_reduced, assignment) == cnf._TRUE_CNF

    # Note: cnf_reduced cannot be TRUE/FALSE, hence all_assignments != ({})
    all_assignments: Iterator[Assignment] = generate_assignments(cnf_reduced)
    head, all_assignments = mit.spy(all_assignments)
    assert head != {}, 'Empty assignment generated.'

    satisfying_assignments: Iterator[Assignment]
    satisfying_assignments = filter(assigns_cnf_to_true, all_assignments)

    return any(satisfying_assignments)


def cnf_pysat_satcheck(cnf_instance: cnf.Cnf) -> bool:
    """Use the `pysat` library's Minisat22 solver to sat-check a Cnf.

    Args:
       cnf_instance (:obj:`cnf.Cnf`)

    Return:
       If the Cnf is Satisfiable return ``True`` else return ``False``.

    """
    from pysat.solvers import Minisat22  # type: ignore  # pylint: disable=import-outside-toplevel  # noqa

    try:
        with Minisat22(cnf_instance) as minisat_solver:
            return cast(bool, minisat_solver.solve())
    except ValueError:
        # The Cnf was probably not in reduced form.
        # Reduce and try again
        cnf_reduced: cnf.Cnf
        cnf_reduced = cnf.tautologically_reduce_cnf(cnf_instance)

        if cnf_reduced == cnf._TRUE_CNF:
            return True
        if cnf_reduced == cnf._FALSE_CNF:
            return False
        with Minisat22(cnf_reduced) as minisat_solver:
            return cast(bool, minisat_solver.solve())


def cnf_to_dimacs(cnf_instance: cnf.Cnf) -> str:
    """Convert a Cnf to DIMACS format.

    The Cnf is tautologically reduced first so as to not contain TRUE or FALSE lits.
    Args:
       cnf_instance (:obj:`cnf.Cnf`)

    Return:
       A string which consists of lines. Each line is a Clause of the Cnf ending with
       zero. Each lit in the Clause is written with a space delimiter.

       After tautological reduction, if the Cnf reduced to TRUE or FALSE then return a
       string that will be correctly interpreted as such.

    """
    cnf_reduced: cnf.Cnf
    cnf_reduced = cnf.tautologically_reduce_cnf(cnf_instance)

    if cnf_reduced == cnf._TRUE_CNF:
        return ''  # A Clause that is always satisfied
    if cnf_reduced == cnf._FALSE_CNF:
        return '0'  # A Clause that can never be satisfied

    clause_strs: Iterator[Iterator[str]]
    clause_strs = map(lambda clause: map(str, clause), cnf_reduced)

    clause_strs_with_tails: Iterator[str]
    clause_strs_with_tails = map(lambda clause_str: ' '.join(clause_str) + ' 0',
                                 clause_strs)

    return '\n'.join(clause_strs_with_tails)


def cnf_minisat_satcheck(cnf_instance: cnf.Cnf) -> bool:
    """Use the `subprocess` library to call minisat.c solver to sat-check a Cnf.

    minisat.c should be correctly installed for this to work.

    Args:
       cnf_instance (:obj:`cnf.Cnf`)

    Return:
       If the Cnf is Satisfiable return ``True`` else return ``False``.

    """
    cnf_dimacs: str
    cnf_dimacs = cnf_to_dimacs(cnf_instance)

    output: str = subprocess.run(['minisat', '-rnd-init', '-verb=0'],
                                 input=cnf_dimacs,
                                 text=True,
                                 capture_output=True,
                                 shell=True,
                                 check=False).stdout

    result: str = output.split()[-1]
    if result == 'SATISFIABLE':
        return True
    if result == 'UNSATISFIABLE':
        return False
    # This is an unreachable.
    raise RuntimeError('Unexpected output from minisat.', output)   # pragma: no cover


# Functions for generating Cnfs from MHGraphs
# ===========================================


def lits_from_vertex(vertex: graph.Vertex) -> tuple[cnf.Lit, cnf.Lit]:
    """Return a Lit as well as its negation from a Vertex.

    Args:
       vertex (:obj:`graph.Vertex`)

    Returns:
       ``vertex`` and ``cnf.neg(vertex)`` after casting each to cnf.Lit.

    """
    positive_lit: cnf.Lit = cnf.lit(vertex)
    return positive_lit, cnf.neg(positive_lit)


def clauses_from_hedge(hedge: mhgraph.HEdge) -> tuple[cnf.Clause, ...]:
    r"""Return all Clauses supported on a HEdge.

    Args:
       hedge (:obj:`mhgraph.HEdge`)

    Return:
       An iterator of cnf.Clause consisting of the :math:`2^{|\texttt{hedge}|}` Clauses
       that are supported on ``hedge``.

    """
    lits_positive_and_negative: Iterator[tuple[cnf.Lit, cnf.Lit]]
    lits_positive_and_negative = map(lits_from_vertex, hedge)

    lit_combinations: Iterator[tuple[cnf.Lit, ...]]
    lit_combinations = it.product(*lits_positive_and_negative)

    return tuple(map(cnf.clause, lit_combinations))


def cnfs_from_hedge(hedge: mhgraph.HEdge, multiplicity: int) -> Iterator[cnf.Cnf]:
    r"""Return all Cnfs supported on a HEdge with multiplicity.

    Args:
       hedge (:obj:`mhgraph.HEdge`)
       multiplicity (:obj:`int`): an integer in the range
          :math:`\{1, \ldots, 2^{|hedge|}\}`.

    Returns:
       An iterator of cnf.Cnf consisting of the :math:`\binom{2^{|hedge|}}{multiplicity}`
       Cnfs supported on a HEdge ``hedge`` with multiplicity ``multiplicity``.

    Edge case:
       Returns an empty iterator if ``multiplicity`` greater than :math:`2^{|hedge|}`.

    Raises:
       ValueError if ``multiplicity`` is less than 1.

    """
    clause_possibilities: tuple[cnf.Clause, ...]
    clause_possibilities = clauses_from_hedge(hedge)

    clause_tuples: Iterator[tuple[cnf.Clause, ...]]
    clause_tuples = it.combinations(clause_possibilities, r=multiplicity)

    return map(cnf.cnf, clause_tuples)


def cnfs_from_mhgraph(mhgraph_instance: mhgraph.MHGraph,
                      randomize: bool = True) -> Iterator[cnf.Cnf]:
    r"""Return all Cnfs supported on a MHGraph.

    Args:
       mhgraph_instance (:obj:`mhgraph.MHGraph`)
       randomize (:obj:`bool`): if True (default) then return all cnfs in a
          shuffled order.

    Returns:
       An iterator of cnf.Cnf consisting of the
       :math:`\displaystyle\prod_{hedge}\binom{2^{|hedge|}}{multiplicity}` Cnfs supported
       on the MHGraph ``mhgraph_instance``.

    Edge case:
       If `mhgraph_instance` is over-saturated (i.e. if it has a HEdge with multiplicity
       greater than :math:`2^{|hedge|}`, then this function returns an empty iterator.
    """
    cnf_iterators: Iterator[Iterator[cnf.Cnf]]
    cnf_iterators = it.starmap(cnfs_from_hedge, mhgraph_instance.items())

    # Iterator[tuple[cnf.Cnf, ...]] <: Iterator[tuple[frozenset[cnf.Clause], ...]]
    cnf_tuples: Iterator[tuple[cnf.Cnf, ...]]
    cnf_tuples = it.product(*cnf_iterators)

    clause_frozensets: Iterator[frozenset[cnf.Clause]]
    clause_frozensets = it.starmap(frozenset.union, cnf_tuples)

    if not randomize:
        return map(cnf.cnf, clause_frozensets)

    return map(cnf.cnf, mit.random_permutation(clause_frozensets))


def number_of_cnfs(mhgraph_instance: mhgraph.MHGraph) -> int:
    """Return the number of Cnfs supported on a MHGraph.

    Returns `0` in case of over-saturated graphs."""
    return math.prod(math.comb(2**len(h), m) for h, m in mhgraph_instance.items())  # type: ignore


# Functions for Checking Satisfiability of MHGraphs
# =================================================


def mhgraph_bruteforce_satcheck(mhgraph_instance: mhgraph.MHGraph,
                                randomize: bool = True) -> bool:
    """Use brute-force to check satisfiability of a MHGraph.

    .. note::
       Brute-forcing is the most sub-optimal strategy
       possible. Do not use this function on large MHGraphs. (Anything
       more than 6 Vertices or 6 HEdges is large.)

    Args:
       mhgraph_instance (:obj:`mhgraph.MHGraph`)
       randomize (:obj:`bool`): if True (default) then generate all cnfs in
          a shuffled order.

    Return:
       ``True`` if ``mhgraph_instance`` is satisfiable, else return ``False``.

    """
    if number_of_cnfs(mhgraph_instance):
        return all(map(cnf_bruteforce_satcheck,
                       cnfs_from_mhgraph(mhgraph_instance, randomize=randomize)))
    return False


@ft.lru_cache
def mhgraph_pysat_satcheck(mhgraph_instance: mhgraph.MHGraph, randomize: bool = True) -> bool:
    """Use the `pysat` library's Minisat22 solver to check satisfiability of a MHGraph.

    Args:
       mhgraph_instance (:obj:`mhgraph.MHGraph`)
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


def mhgraph_minisat_satcheck(mhgraph_instance: mhgraph.MHGraph) -> bool:
    """Use the `subprocess` library to launch `minisat.c` and sat-check a MHGraph.

    Args:
       mhgraph_instance (:obj:`mhgraph.MHGraph`)

    Return:
       ``True`` if ``mhgraph_instance`` is satisfiable, else return ``False``.

    """
    if number_of_cnfs(mhgraph_instance):
        return all(map(cnf_minisat_satcheck, cnfs_from_mhgraph(mhgraph_instance)))
    return False


# Function for generating MHGraphs from Cnfs
# ==========================================


def mhgraph_from_cnf(cnf_instance: cnf.Cnf) -> mhgraph.MHGraph:
    """Return the MHGraph that supports a given Cnf.

    This function first tautologically reduces the Cnf using
    :obj:`cnf.tautologically_reduce_cnf()`.
    This ensures no self-loops or collapsed HEdges in the final MHGraph.

    Args:
       cnf_instance (:obj:`cnf.Cnf`): a Cnf that does not tautologically reduce to
          ``cnf.cnf([[cnf.TRUE]])`` or ``cnf.cnf([[cnf.FALSE]])``.

    Return:
       The MHGraph that supports ``cnf_instance``.

    Raises:
       ValueError: If ``cnf_instance`` is trivially `True` or trivially `False`
          after performing tautological reductions.

    """
    reduced_cnf: cnf.Cnf = cnf.tautologically_reduce_cnf(cnf_instance)

    if reduced_cnf in {cnf._TRUE_CNF, cnf._FALSE_CNF}:
        raise ValueError('Cnf reduced to trivial True/False & has no supporting MHGraph.')

    # Iterator[frozenset[cnf.Lit]] <: Iterator[Collection[int]]
    cnf_with_abs_variables: Iterator[frozenset[cnf.Lit]]
    cnf_with_abs_variables = map(lambda c: frozenset(map(cnf.absolute_value, c)),
                                 reduced_cnf)

    return mhgraph.mhgraph(list(cnf_with_abs_variables))


# Function for simplifying MHGraphs before sat-solving
# ====================================================


def is_oversaturated(mhg: mhgraph.MHGraph) -> bool:
    """Return True if any edge of mhg of size n has multiplicity more than 2^n."""
    return any(mult > 2**len(hedge) for hedge, mult in mhg.items())


def simplify_at_leaves(mhg: mhgraph.MHGraph) -> Union[bool, mhgraph.MHGraph]:
    """If the graph contains a degree-one vertex, then remove that HEdge.

    This results in a graph that is equisatisfiable to the first.

    Edge cases:

       * if every HEdges is a leaf edge, then return True.

       * In the limit, the resulting mhgraph is guaranteed to have all vertices be
         degree >= 2.

    """
    leaf_vertex: graph.Vertex = mhgraph.pick_min_degree_vertex(mhg)
    if mhgraph.degree(leaf_vertex, mhg) > 1:
        return mhg
    logger.trace(f'{leaf_vertex = }')
    sphr: tuple[mhgraph.HEdge, ...] = mhgraph.sphr(mhg, leaf_vertex)
    logger.trace(f'simplified to {sphr}')
    return mhgraph.mhgraph(sphr) if sphr else True


def has_double_loop(mhg: mhgraph.MHGraph) -> bool:
    """Return True iff mhg has a double loop."""
    double_loop_graph: mhgraph.MHGraph
    double_loop_graph = mhgraph.mhgraph([[37], [37]])

    return morph.subgraph_search(double_loop_graph, mhg, return_all=False)[0]


def supports_single_loop(mhg: mhgraph.MHGraph) -> Union[bool, graph.Vertex]:
    """Return a vertex that supports a loop in mhg.

    If no such vertex exists, return False.

    """
    loops: list[graph.Vertex]
    loops = [vertex for vertex in mhgraph.vertices(mhg) if frozenset([vertex]) in mhg]
    logger.trace(f'{loops = }')
    return loops[0] if loops else False


@ft.lru_cache
def simplify_at_loops(mhg: mhgraph.MHGraph) -> Union[bool, mhgraph.MHGraph]:
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

    sphr: tuple[mhgraph.HEdge, ...]
    sphr = mhgraph.sphr(mhg, vertex)
    logger.trace(f'{sphr = }')

    link: tuple[mhgraph.HEdge, ...]
    link = mhgraph.link(mhg, vertex)
    logger.trace(f'{link = }')

    if not link and not sphr:
        # iff mhg is isomorphic to a bunch of loops at the verrtex.  But since we
        # already ruled out double loops (or higher), we can be sure that mhg has
        # only one loop.
        assert len(list(mhg.elements())) == 1
        logger.trace(f'{mhg} simplified to True')
        return True

    sphr_link: mhgraph.MHGraph = mhgraph.graph_union(sphr, link)
    logger.success(f'{mhg} simplified to {sphr_link}')
    return sphr_link


@ft.lru_cache
def simplify_at_leaves_and_loops(mhg: mhgraph.MHGraph) -> Union[bool, mhgraph.MHGraph]:
    """Call both simplify_at_leaves() and simplify_at_loops().

    This results in a graph that is equisatisfiable to the first.

    """
    mhg_simp = simplify_at_leaves(mhg)
    if isinstance(mhg_simp, bool):
        return mhg_simp

    if mhg_simp != mhg:
        return simplify_at_leaves_and_loops(mhg_simp)

    mhg_simp = simplify_at_loops(mhg_simp)
    if isinstance(mhg_simp, bool):
        return mhg_simp

    if mhg_simp != mhg:
        return simplify_at_leaves_and_loops(mhg_simp)

    # Fixed-point reached.
    return mhg_simp


if __name__ == '__main__':
    logger.info('We have several different sat-solvers implemented here.')
    logger.info(">>> cnf_bruteforce_satcheck(cnf([[1, 2], [-1, 2], [1, -2]]))")
    logger.success(cnf_bruteforce_satcheck(cnf.cnf([[1, 2], [-1, 2], [1, -2]])))
    logger.info('\n')
    logger.info('An example which is unsatisfiable:')
    logger.info(">>> cnf_pysat_satcheck(cnf([[1, 2], [1, -2], [-1, 2], [-1, -2]]))")
    logger.success(cnf_pysat_satcheck(cnf.cnf([[1, 2], [1, -2], [-1, 2], [-1, -2]])))
    logger.info('\n')
    logger.info('mhgraph_pysat_satcheck() finds all Cnfs supported on a MHGraph\n'
                + ' '*61 + 'and then sat-checks them using the pysat satchecker.')
    logger.info('>>> mhgraph_pysat_satcheck()(mhgraph.mhgraph([[1, 2], [2, 3]]))')
    logger.success(mhgraph_pysat_satcheck((mhgraph.mhgraph([[1, 2], [2, 3]]))))
    logger.info('True output indicates that this MHGraph only supports satisfiable Cnfs.')
    logger.info('\n')
    logger.info('Given a Cnf we can also ask for its supporting MHGraph.')
    logger.info('>>> mhgraph_from_cnf(cnf.cnf([[1, -2], [2, 3, 4], [1, 2]]))')
    logger.success(mhgraph_from_cnf(cnf.cnf([[1, -2], [2, 3, 4], [1, 2]])))

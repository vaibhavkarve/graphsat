#!/usr/bin/env python3.8
"""An implementation of the Local graph rewriting algorithm."""

# Imports from standard library.
import functools as ft
import itertools as it
from collections import defaultdict
from typing import Any, Iterator, Sequence, cast

# Imports from third-paty modules.
import more_itertools as mit
from colorama import init
from loguru import logger
from tabulate import tabulate

# Imports from local modules.
import graphsat.graph_collapse as gcol
import graphsat.mhgraph as mhg
import graphsat.operations as op
# Importing because single-dispatch does not do well with imported
# types.
from normal_form import cnf, sat, prop
from graphsat import graph, translation
from graphsat.mhgraph import HEdge, MHGraph, mhgraph



def get_head_and_cnfs(list_hedges: tuple[mhg.HEdge, ...]) \
        -> tuple[list[cnf.Cnf], Iterator[cnf.Cnf]]:
    """Return first and all Cnfs supported on a list of HEdges."""
    cnfs: Iterator[cnf.Cnf]
    cnfs = translation.cnfs_from_mhgraph(mhg.mhgraph(list_hedges))
    return mit.spy(cnfs)


def decompose_pair(hyp1_hyp2: tuple[list[mhg.HEdge], list[mhg.HEdge]]) \
        -> bool:
    """Return True iff either part is satisfiable."""
    return any(map(decompose, map(mhg.mhgraph, hyp1_hyp2)))


def satcheck_independent(sphr_hyp1: MHGraph, sphr_hyp2: MHGraph) -> bool:
    """Satcheck as if the pieces are indpendent.

    This is a heuristic check.  The entangled version is SAT if this
    function returns True.
    """
    logger.trace(f'Start heuristic for {sphr_hyp1} ∨ {sphr_hyp2}')
    return decompose(sphr_hyp1) or decompose(sphr_hyp2)


def satcheck_entangled(cnfs_sphr: Iterator[cnf.Cnf],
                       cnfs_hyp1: Iterator[cnf.Cnf],
                       cnfs_hyp2: list[cnf.Cnf]) -> bool:
    """Satcheck entangled decomposition terms.

    Return True iff ∀xₛ ∈ cnfs_sphr, ∀xₕ₁ ∈ cnfs_hyp1 and ∀xₕ₂ ∈
    cnfs_hyp2 we have (xₛ ∧ xₕ₁) ∼ ⊤ *or* (xₛ ∧ xₕ₂) ∼ ⊤.
    """
    cnf_satcheck = sat.cnf_pysat_satcheck

    for x_sph, x_hyp1 in it.product(cnfs_sphr, cnfs_hyp1):
        x_sph_hyp1: cnf.Cnf = prop.cnf_and_cnf(x_sph, x_hyp1)

        if not cnf_satcheck(x_sph_hyp1):
            for x_hyp2 in cnfs_hyp2:
                x_sph_hyp2: cnf.Cnf = prop.cnf_and_cnf(x_sph, x_hyp2)
                if not cnf_satcheck(x_sph_hyp2):
                    return False
    return True


def compute_all_two_partitions_of_link(mhg_: MHGraph, vertex: graph.Vertex,
                                       guarantee_nonempty: bool = True) \
        -> Iterator[tuple[list[mhg.HEdge], list[mhg.HEdge]]]:
    """Compute the link and then all nonempty 2-paritions of the link."""
    link: tuple[mhg.HEdge, ...] = mhg.link(mhg_, vertex)
    logger.trace(f'{link = }')

    # because link = [] iff mhg_ only has loops incident at vertex.
    assert link, 'Link should be nonempty.'

    if guarantee_nonempty:
        # because user is ecpected to simplify at all degree 1 vertices.`
        assert len(link) > 1, ('Simplify graph using '
                               ' `translation.simplify_at_leaves_and_loops` or'
                               ' set the guarantee_nonempty flag to False.')


    # All 2-partitions of the link. Guaranteed to be a nonempty iter if
    # guarantee_nonempty is set to True (default).
    return cast(Iterator[tuple[list[mhg.HEdge], list[mhg.HEdge]]],
                mit.set_partitions(link, 2))


def local_rewrite(mhg_: MHGraph,
                  vertex: graph.Vertex = graph.vertex(1),
                  print_full: bool = False) -> dict[Any, Any]:
    """Rewrite under the assumption that the graph is only partially known.

    This function will perform a local rewrite at vertex while only affecting
    edges incident on that vertex. It will assume that `mhg_` only represents a
    part of the full graph.

    The result is a dict of Cnfs grouped by their MHGraphs. Since some of
    these Cnf-sets are completely covered by a single MHGraph, wherever
    possible, we replace entire sets of Cnfs with smaller MHGraphs that are
    created in the rewrite.

    If `print_full` is True then print the full table, else (default) print
    only the column headers and complete/incomplete.
    """
    extra_hedge: mhg.HEdge = mhg.hedge([999])

    sphr: set[mhg.HEdge] = set(mhg.sphr(mhg_, vertex))
    sphr = sphr | {extra_hedge}
    logger.trace(f'            sphr = {sphr - {extra_hedge}}')
    sphr_mhg_: mhg.MHGraph = mhg.mhgraph(sphr)

    two_partitions: Iterator[tuple[list[mhg.HEdge], list[mhg.HEdge]]]
    two_partitions = compute_all_two_partitions_of_link(mhg_, vertex)

    rewritten_cnfs: set[cnf.Cnf] = set()
    for hyp1, hyp2 in two_partitions:
        hyp1_hyp2: set[cnf.Cnf] = op.graph_or(mhgraph(hyp1), mhgraph(hyp2))
        sphr_hyp: set[cnf.Cnf] = op.graph_and(sphr_mhg_, hyp1_hyp2)

        rewritten_cnfs |= sphr_hyp

    #with mp.Pool() as pool:
    #    rewritten_cnfs = pool.map(csimp.reduce_cnf, rewritten_cnfs)

    grouping: dict[Any, Any] = gcol.create_grouping(set(rewritten_cnfs))

    if not print_full:
        grouping_new = defaultdict(list)
        for k, v in grouping.items():
            if v == {'Complete'}:
                grouping_new['Complete'].append(k)
            else:
                grouping_new['Incomplete'].append(k)
        print(dict(grouping_new))
    else:
        print('\n', tabulate(grouping,
                             headers=list(grouping.keys()),
                             showindex=True))
    return grouping


def satcheck_partition(mhg_: mhg.MHGraph,
                       sphr: Sequence[mhg.HEdge],
                       hyp1_hyp2: tuple[list[HEdge], list[HEdge]]) -> bool:
    """Return true if the partition term is satisfiable."""
    hyp1: list[HEdge]
    hyp2: list[HEdge]
    hyp1, hyp2 = hyp1_hyp2

    hyp1_oversaturated: bool = translation.is_oversaturated(mhg.mhgraph(hyp1))
    hyp2_oversaturated: bool = translation.is_oversaturated(mhg.mhgraph(hyp2))

    if hyp1_oversaturated and hyp2_oversaturated:
        logger.trace(f'{hyp1 = } and {hyp2 = } are both over-saturated.')
        return False

    sphr_union_hyp1: MHGraph = mhg.graph_union(sphr, tuple(hyp1))
    sphr_union_hyp2: MHGraph = mhg.graph_union(sphr, tuple(hyp2))

    if hyp1_oversaturated:
        logger.trace(f'{hyp1 = } is over-saturated.')
        if not decompose(sphr_union_hyp2):
            return False
        return True

    if hyp2_oversaturated:
        logger.trace(f'{hyp2 = } is over-saturated.')
        if not decompose(sphr_union_hyp1):
            return False
        return True

    # Perform heuristic check
    if satcheck_independent(sphr_union_hyp1, sphr_union_hyp2):
        logger.trace(f'{sphr_union_hyp1} ∨ {sphr_union_hyp2} is SAT, '
                     'determined by heuristic check.')
        return True

    cnfs_hyp1: Iterator[cnf.Cnf] = translation.cnfs_from_mhgraph(mhg.mhgraph(hyp1))
    cnfs_hyp2: Iterator[cnf.Cnf] = translation.cnfs_from_mhgraph(mhg.mhgraph(hyp2))
    cnfs_sphr: Iterator[cnf.Cnf] = translation.cnfs_from_mhgraph(mhg.mhgraph(sphr))

    if not satcheck_entangled(cnfs_sphr, cnfs_hyp1, list(cnfs_hyp2)):
        logger.trace(f'{mhg_} is UNSAT, determined by reduce_entangled()')
        print(f'{mhg_} is UNSAT, determined by reduce_entangled()')
        return False
    return True


def decompose_at_vertex(mhg_: MHGraph, vertex: graph.Vertex,
                        hyperbolic_only: bool = False) -> bool:
    """Decompose mhg at a specified vertex."""
    # sphr is empty iff every HEdge of mhg is incident on vertex.
    sphr: tuple[mhg.HEdge, ...] = mhg.sphr(mhg_, vertex)
    logger.trace(f'       {sphr = }')

    two_partitions: Iterator[tuple[list[HEdge], list[HEdge]]]
    two_partitions = compute_all_two_partitions_of_link(mhg_, vertex)

    if hyperbolic_only:
        # Filter out only maximally hyperbolic two_partitions.
        two_partitions = filter(lambda parts: abs(len(parts[0])-len(parts[1])) <= 1,
                                two_partitions)

    if not sphr:
        # iff every HEdge of mhg is incident on vertex.
        # i.e. if mhg is a star-graph around the vertex.
        return all(decompose_pair(hyp1_hyp2) for hyp1_hyp2 in two_partitions)

    if translation.is_oversaturated(mhg.mhgraph(sphr)):
        logger.trace(f'{sphr =} is over-saturated.')
        return False

    # Conjunction over all partitions.  hyp1 and hyp2 guaranteed to be
    # nonempty.
    status_partitions = map(lambda hyp1_hyp2: satcheck_partition(mhg_, sphr, hyp1_hyp2),
                            two_partitions)
    if not all(status_partitions):
        return False

    logger.trace(f'{mhg_} is SAT')
    print(f'{mhg_} is SAT')
    return True


@ft.lru_cache(maxsize=1024)
def decompose(mhg_: MHGraph, hyperbolic_only: bool = False) -> bool:
    """Decompose using entangled graph-rewrite terms at max-degree vertex.

    We decompose and then reduce using `reduce_entangled()` before returning
    the result.
    """
    mhg_simp = translation.simplify_at_leaves_and_loops(mhg_)
    if isinstance(mhg_simp, bool):
        # mhg either a) has two or more loops at a vertex, or b) is
        # isomorphic to a single-loop graph or c) has only leaf edges.
        logger.trace(f'{mhg_} is {"SAT" if mhg_simp else "UNSAT"},'
                     ' determined by simplifying at leaves and loops.')
        return mhg_simp

    mhg_ = mhg_simp
    # mhg_ now has no loops.
    assert all(len(hedge) > 1 for hedge in mhg_.keys()), \
        'simplify_at_leaves_and_loops() failed to simplify all loops.'
    # mhg_ now has no leaves.
    assert all(mhg.degree(v, mhg_) > 1 for v in mhg.vertices(mhg_)), \
        'simplify_at_leaves_and_liips() failed to simplify all leaves.'

    vert: graph.Vertex = mhg.pick_max_degree_vertex(mhg_)
    logger.trace('')
    logger.trace(f'                {mhg_ = }')
    logger.trace(f'                {vert = }')

    return decompose_at_vertex(mhg_, vert, hyperbolic_only=hyperbolic_only)


def square(a: int, b: int, c: int, d: int, x: int) -> mhg.MHGraph:  # pylint: disable=invalid-name
    """Create a square of four hedges of size 3."""
    return mhg.mhgraph([[a, b, x], [b, c, x], [c, d, x], [d, a, x]])


if __name__ == "__main__":  # pragma: no cover
    import sys
    from time import time
    logger.remove()
    logger.add(sys.stdout, level=0)
    init()  # for initializing terminal coloring
    time0 = time()
    # (124 ∧ 134 ∧ 135 ∧ 152)
    G = mhg.mhgraph([[1,2,4], [1,3,4], [1,3,5], [1,2,5]])
    lrw = local_rewrite(G, graph.vertex(1), False)
    print()
    print(tabulate(lrw))
    logger.info(f"Total time taken = {round(time() - time0, 2)}s")

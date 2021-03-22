#!/usr/bin/env python3.9
"""An implementation of the Local graph rewriting algorithm."""

# Imports from standard library.
from collections import defaultdict
import functools as ft
import itertools as it
import multiprocessing as mp
from typing import Any, Collection, Iterator

# Imports from third-paty modules.
from colorama import init  # type: ignore
from loguru import logger
import more_itertools as mit
from tabulate import tabulate
from tqdm import tqdm  # type: ignore

# Imports from local modules.
import cnf
import mhgraph
import operations as op
from prop import cnf_and_cnf
import sat

# Importing because single-dispatch does not do well with imported
# types.
from mhgraph import MHGraph

import cnf_simplify as csimp
import graph_collapse as gcol


def get_head_and_cnfs(list_hedges: tuple[mhgraph.HEdge, ...]) \
        -> tuple[cnf.Cnf, Iterator[cnf.Cnf]]:
    """Return first and all Cnfs supported on a list of HEdges."""
    cnfs: Iterator[cnf.Cnf]
    cnfs = sat.cnfs_from_mhgraph(mhgraph.mhgraph(list_hedges))
    return mit.spy(cnfs)  # type: ignore


def decompose_pair(hyp1_hyp2: tuple[list[mhgraph.HEdge], list[mhgraph.HEdge]]) \
        -> bool:
    """Return True iff either part is satisfiable."""
    return any(map(decompose, map(mhgraph.mhgraph, hyp1_hyp2)))


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
        x_sph_hyp1: cnf.Cnf = cnf_and_cnf(x_sph, x_hyp1)

        if not cnf_satcheck(x_sph_hyp1):
            for x_hyp2 in cnfs_hyp2:
                x_sph_hyp2: cnf.Cnf = cnf_and_cnf(x_sph, x_hyp2)
                if not cnf_satcheck(x_sph_hyp2):
                    return False
    return True


def compute_all_two_partitions(mhg: MHGraph, vertex: mhgraph.Vertex) \
        -> Iterator[tuple[list[mhgraph.HEdge], list[mhgraph.HEdge]]]:
    """Compute the link and then all nonempty 2-paritions of the link.
    """
    link: tuple[mhgraph.HEdge, ...] = mhgraph.link(mhg, vertex)
    logger.trace(f'{link = }')

    # because link = [] iff mhg only has loops incident at vertex.
    assert link, 'Link should be nonempty.'
    # because we simplified at all degree 1 vertices.
    assert len(link) > 1, 'Link should have more than one element.'

    # All 2-partitions of the link. Guaranteed to be a nonempty iter.
    return mit.set_partitions(link, 2)


def local_rewrite(mhg: MHGraph,
                  vertex: mhgraph.Vertex = mhgraph.vertex(1),
                  print_full: bool = False) -> dict[Any, Any]:
    """Rewrite under the assumption that the graph is only partially known.

    This function will perform a local rewrite at vertex while only affecting
    edges incident on that vertex. It will assume that `mhg` only represents a
    part of the full graph.

    The result is a dict of Cnfs grouped by their MHGraphs. Since some of
    these Cnf-sets are completely covered by a single MHGraph, wherever
    possible, we replace entire sets of Cnfs with smaller MHGraphs that are
    created in the rewrite.

    If `print_full` is True (default) then print the full table, else print
    only the column headers and complete/incomplete.
    """
    extra_hedge: mhgraph.HEdge = mhgraph.hedge([999])

    sphr: set[mhgraph.HEdge] = set(mhgraph.sphr(mhg, vertex))
    sphr = sphr | {extra_hedge}
    logger.trace(f'            sphr = {sphr - {extra_hedge}}')
    sphr_mhg: mhgraph.MHGraph = mhgraph.mhgraph(sphr)


    two_partitions: Iterator[tuple[list[mhgraph.MHGraph], list[mhgraph.MHGraph]]]
    two_partitions = compute_all_two_partitions(mhg, vertex)

    rewritten_cnfs: set[cnf.Cnf] = set()
    for hyp1, hyp2 in two_partitions:
        hyp1_hyp2: set[cnf.Cnf] = op.graph_or(hyp1, hyp2)
        sphr_hyp: set[cnf.Cnf] = op.graph_and(sphr_mhg, hyp1_hyp2)

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


def satcheck_partition(mhg: mhgraph.MHGraph,
                       sphr: Collection[mhgraph.HEdge],
                       hyp1_hyp2: tuple[list[mhgraph.MHGraph], list[mhgraph.MHGraph]]):
    """Return true if the partition term is satisfiable."""
    hyp1, hyp2 = hyp1_hyp2

    hyp1_oversaturated: bool = sat.is_oversaturated(mhgraph.mhgraph(hyp1))
    hyp2_oversaturated: bool = sat.is_oversaturated(mhgraph.mhgraph(hyp2))

    if hyp1_oversaturated and hyp2_oversaturated:
        logger.trace(f'{hyp1 = } and {hyp2 = } are both over-saturated.')
        return False

    sphr_union_hyp1: MHGraph = mhgraph.graph_union(sphr, tuple(hyp1))
    sphr_union_hyp2: MHGraph = mhgraph.graph_union(sphr, tuple(hyp2))

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

    cnfs_hyp1: Iterator[cnf.Cnf] = sat.cnfs_from_mhgraph(mhgraph.mhgraph(hyp1))
    cnfs_hyp2: Iterator[cnf.Cnf] = sat.cnfs_from_mhgraph(mhgraph.mhgraph(hyp2))
    cnfs_sphr: Iterator[cnf.Cnf] = sat.cnfs_from_mhgraph(mhgraph.mhgraph(sphr))

    if not satcheck_entangled(cnfs_sphr, cnfs_hyp1, list(cnfs_hyp2)):
        logger.trace(f'{mhg} is UNSAT, determined by reduce_entangled()')
        print(f'{mhg} is UNSAT, determined by reduce_entangled()')
        return False
    return True


def decompose_at_vertex(mhg: MHGraph, vertex: mhgraph.Vertex, hyperbolic_only=False) -> bool:
    """Decompose mhg at a specified vertex."""
    # sphr is empty iff every HEdge of mhg is incident on vertex.
    sphr: tuple[mhgraph.HEdge, ...] = mhgraph.sphr(mhg, vertex)
    logger.trace(f'       {sphr = }')

    two_partitions: Iterator[tuple[list[mhgraph.MHGraph], list[mhgraph.MHGraph]]]
    two_partitions = compute_all_two_partitions(mhg, vertex)

    if hyperbolic_only:
        # Filter out only maximally hyperbolic two_partitions.
        two_partitions = filter(lambda parts: abs(len(parts[0])-len(parts[1])) <= 1,
                                two_partitions)

    if not sphr:
        # iff every HEdge of mhg is incident on vertex.
        # i.e. if mhg is a star-graph around the vertex.
        return all(decompose_pair(hyp1_hyp2) for hyp1_hyp2 in two_partitions)

    if sat.is_oversaturated(mhgraph.mhgraph(sphr)):
        logger.trace(f'{sphr =} is over-saturated.')
        return False

    # Conjunction over all partitions.  hyp1 and hyp2 guaranteed to be
    # nonempty.
    status_partitions = map(lambda hyp1_hyp2: satcheck_partition(mhg, sphr, hyp1_hyp2),
                            two_partitions)
    if not all(status_partitions):
        return False

    logger.trace(f'{mhg} is SAT')
    print(f'{mhg} is SAT')
    return True


@ft.lru_cache(1024)
def decompose(mhg: MHGraph, hyperbolic_only=False) -> bool:
    """Decompose using entangled graph-rewrite terms at max-degree vertex.

    We decompose and then reduce using `reduce_entangled()` before returning
    the result.
    """
    mhg_simp = sat.simplify_at_leaves_and_loops(mhg)
    if isinstance(mhg_simp, bool):
        # mhg either a) has two or more loops at a vertex, or b) is
        # isomorphic to a single-loop graph or c) has only leaf edges.
        logger.trace(f'{mhg} is {"SAT" if mhg_simp else "UNSAT"},'
                     ' determined by simplifying at leaves and loops.')
        return mhg_simp

    mhg = mhg_simp
    # mhg now has no loops.
    assert all(len(hedge) > 1 for hedge in mhg.keys()), \
        'simplify_at_leaves_and_loops() failed to simplify all loops.'
    # mhg now has no leaves.
    assert all(mhgraph.degree(v, mhg) > 1 for v in mhgraph.vertices(mhg)), \
        'simplify_at_leaves_and_liips() failed to simplify all leaves.'

    vert: mhgraph.Vertex = mhgraph.pick_max_degree_vertex(mhg)
    logger.trace('')
    logger.trace(f'                {mhg  = }')
    logger.trace(f'                {vert = }')

    return decompose_at_vertex(mhg, vert, hyperbolic_only=hyperbolic_only)


def square(a: int, b: int, c: int, d: int, x: int) -> mhgraph.MHGraph:  # pylint: disable=invalid-name
    """Create a square of four hedges of size 3."""
    return mhgraph.mhgraph([[a, b, x], [b, c, x], [c, d, x], [d, a, x]])


if __name__ == "__main__":
    from time import time
    import sys
    logger.remove()
    logger.add(sys.stdout, level=0)
    init()  # for initializing terminal coloring
    time0 = time()
    G = mhgraph.mhgraph([[1,2,3], [4,5,6], [1,4,5], [1,2,5], [2,5,6], [2,3,6], [1,4,6], [1,3,6]])
    dec: bool = decompose(G)
    print()
    logger.success(dec)
    print()
    logger.info(f"Total time taken = {round(time() - time0, 2)}s")

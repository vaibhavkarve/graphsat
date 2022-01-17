#!/usr/bin/env python3.9
"""Computations at the module level.

1. satcheck_triangulations
"""
from typing import Iterator

from loguru import logger
from tqdm import tqdm

import mhgraph as mhg
import operations as op

import dat_management as datm
import graph_collapse as gcol
import graph_rewrite as grw
import reduce_by_rules as rbr


@logger.catch
def satcheck_triangulations(hyperbolic_only=False) -> None:
    """Satcheck triangulations of the disc.

    Input: triangulations.dat
    Output : sat or unsat
    """
    dat: Iterator[mhg.MHGraph] = datm.read_dat('triangulations.dat')
    for triangulation in tqdm(dat):
        tree: rbr.GraphNode = rbr.make_tree(triangulation, None)
        logger.info(f'{triangulation = }')
        print(tree)
        logger.info(f'leaves = {tree.leaves}')
        for leaf in tree.leaves:
            leaf_status: bool = grw.decompose(leaf.graph, hyperbolic_only=hyperbolic_only)
            if not leaf_status:
                logger.error(f'{triangulation} ~ F')
                break
        else:
            logger.success(f'{triangulation} ~ T')


@logger.catch
def compute_graph_or() -> None:
    """Compute the graph_or of two graphs resulting from Graph rewrite."""
    gr1: mhg.MHGraph = mhg.mhgraph([[2,3]])
    gr2: mhg.MHGraph = mhg.mhgraph([[3,4], [4,5]])
    for index, cnf_ in enumerate(op.graph_or(gr1, gr2)):
        print(index, cnf_)
    print()
    gcol.print_grouping_table(op.graph_or(gr1, gr2))


if __name__ == '__main__':
    from time import time

    time0 = time()
    logger.disable('graph_rewrite')
    logger.disable('sat')

    #satcheck_triangulations(hyperbolic_only=True)
    #logger.debug(f'Total time = {round(time() - time0, 2)}s')
    compute_graph_or()
    #grw.local_rewrite(mhg.mhgraph([[1,2,3], [1,3,4], [1,4,5]]), 1, False)

    # Icosahedron
    # [12, 2, 1], [12, 3, 2], [12, 1, 4], [1, 2, 5], [12, 11, 3], [12, 4, 11], [1, 9, 4], [1, 5, 9], [2, 10, 5], [2, 3, 10], [4, 9, 8], [4, 8, 11], [3, 11, 7], [3, 7, 10], [5, 10, 6], [5, 6, 9], [7, 11, 8], [6, 10, 7], [6, 8, 9], [6, 7, 8]

    # Mobius in RP2
    # [1, 2, 3], [3, 2, 6], [4, 6, 1], [4, 1, 2], [5, 2, 6], [5, 6, 1], [1, 5, 3], [3, 6, 4], [4, 2, 5], [5, 3, 4]

    # Klein bottle 242
    # [1,2,3], [3,7,2], [1,5,3], [1,7,5], [1,4,7], [1,6,2], [6,4,2], [1,6,8], [1,4,8], [2,4,8], [6,4,3], [3,7,4], [6,8,5], [6,5,3], [8,2,5], [2,7,5]

    # Torus
    # [1,2,6], [2,6,7], [2,3,7], [3,7,1], [6,7,4], [7,4,5], [7,1,5], [1,5,6], [4,1,2], [4,5,2], [5,2,3], [5,6,3], [6,3,4], [4,3,1]

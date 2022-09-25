#!/usr/bin/env python3.9
"""Module for reducing graphs according to known reduction rules.

All known rules are in this file and are read in the variable
KNOWN_RULES.
"""
import functools as ft
import itertools as it
import multiprocessing as mp
from typing import Any, Iterator, NamedTuple, Optional, cast

import config
import more_itertools as mit
import typer
from loguru import logger

import graphsat.mhgraph as mhg
import graphsat.morphism as morph
import graphsat.sat
from graphsat.cnf import TRUE
from graphsat.graph import Vertex, vertex

# pylint: disable=invalid-name
app = typer.Typer(add_completion=False)



def reduce_all_mhgraph(mhg_list: list[mhg.MHGraph]) -> list[mhg.MHGraph]:
    """Apply rules to all mhgraphs in list."""
    return list(mit.flatten(map(reduce_using_all_rules, mhg_list)))


def criminals_to_reductions(criminals_dat: list[mhg.MHGraph]) -> None:
    """Compute reductions (by all rules) for criminals in criminals DAT.

    Useful for debugging.  Will print criminals and reductions next to one another.
    """
    for crim in criminals_dat:
        reductions = reduce_using_all_rules(crim)
        reduction_strs = map(str, reductions)
        reduction_strs_joined = "\t".join(reduction_strs)
        logger.info(f'{crim} reduced to {reduction_strs_joined}')


def compute_all_reductions(criminals_dat: Iterator[mhg.MHGraph]) \
        -> Iterator[mhg.MHGraph]:
    """Compute all reductions and then remove duplicates."""
    reductions: list[list[mhg.MHGraph]]
    with mp.Pool() as pool:
        reductions = pool.map(reduce_using_all_rules, criminals_dat)

    reductions_flat: Iterator[mhg.MHGraph]
    reductions_flat = mit.flatten(reductions)
    reductions_flat = morph.unique_upto_isom(reductions_flat)
    return reductions_flat


@app.command()
def write_reduced_criminals(v: int = config.ARGDOCS['v'],
                            emin: int = config.ARGDOCS['emin'],
                            emax: int = config.ARGDOCS['emax'],
                            mixed: str = config.ARGDOCS['mixed'],
                            multi: str = config.ARGDOCS['multi']) -> None:
    """Apply reduction rules to criminals.dat and write to criminals_reduced.dat."""
    cli_args: config.ArgsType = (v, emin, emax, mixed, multi)
    logger.disable('graphsat')

    reduce_by_rules_log: str = config.files('reduce_by_rules_log', cli_args)
    logger.add(reduce_by_rules_log, colorize=True, level=0, retention=1)

    criminals_dat: str = config.files('criminals', cli_args)
    criminals_reduced_dat: str = config.files('criminals_reduced', cli_args)

    criminals: Iterator[mhg.MHGraph] = datm.read_dat(criminals_dat)
    reductions: Iterator[mhg.MHGraph] = compute_all_reductions(criminals)

    datm.write_dat(criminals_reduced_dat, reductions)
    config.print_end_message()


if __name__ == '__main__':
    app()
    g: mhg.MHGraph = mhg.mhgraph([[1, 2, 3], [1,3,4], [2,3,4], [1,4,5], [2,4,5]])
    g1: mhg.GraphNode = make_tree(g, None)
    print(g1)
    print(g1.leaves)

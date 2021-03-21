#!/usr/bin/env python3.9
"""Module for reducing graphs according to known reduction rules.

All known rules are in this file and are read in the variable
KNOWN_RULES.
"""
import functools as ft
import itertools as it
import multiprocessing as mp
from typing import Any, cast, Iterator, NamedTuple, Optional

from loguru import logger
import more_itertools as mit  # type: ignore
import typer

from cnf import TRUE
from graph import vertex, Vertex
import mhgraph as mhg
import morphism as morph
import sat

import config
from graph_as_tree import GraphNode

app = typer.Typer(add_completion=False)


# pylint: disable=invalid-name
app = typer.Typer(add_completion=False)


EDGE_SMOOTH = GraphNode(mhg.mhgraph([[1, 2], [1, 3]]),
                        free=vertex(1),
                        children=[mhg.mhgraph([[2, 3]])])

HEDGE_SMOOTH = GraphNode(mhg.mhgraph([[1, 2, 3], [1, 2, 4]]),
                         free=vertex(1),
                         children=[mhg.mhgraph([[2, 3, 4]])])

R1 = GraphNode(mhg.mhgraph([[1, 2, 3], [1, 2]]),
               free=vertex(1),
               children=[mhg.mhgraph([[2, 3]])])

R2 = GraphNode(mhg.mhgraph([[1, 2, 3], [1, 2], [1, 3]]),
               free=vertex(1),
               children=[mhg.mhgraph([[2]]), mhg.mhgraph([[3]])])


R4 = GraphNode(mhg.mhgraph([[1, 2, 3], [1, 2, 4], [1, 3, 4]]),
               free=vertex(1),
               children=[mhg.mhgraph([[2, 3]]),
                         mhg.mhgraph([[2, 4]]),
                         mhg.mhgraph([[3, 4]])])

R5 = GraphNode(mhg.mhgraph([[1, 2, 3], [1, 4]]),
               free=vertex(1),
               children=[mhg.mhgraph([[2, 3, 4]])])

R7 = GraphNode(mhg.mhgraph([[1, 2, 3], [1, 2, 3], [1, 2], [1, 3]]),
               free=vertex(1),
               children=[mhg.mhgraph([[2, 3]]*3)])


LEAF1 = GraphNode(mhg.mhgraph([[1]]),
                  free=vertex(1),
                  children=[])


def pop2(n: int) -> GraphNode:
    """Pop a simple-leaf vertex."""
    assert n > 1
    return GraphNode(mhg.mhgraph([[1, 2]]*n),
                     free=vertex(1),
                     children=[mhg.mhgraph([[2]]*(n//2))])


def pop3(n: int) -> GraphNode:
    """Pop a hyper-leaf vertex."""
    assert n > 1
    return GraphNode(mhg.mhgraph([[1, 2, 3]]*n),
                     free=vertex(1),
                     children=[mhg.mhgraph([[2, 3]]*(n//2))])


KNOWN_RULES = [EDGE_SMOOTH, HEDGE_SMOOTH] \
    + [R1, R2, R4, R5, R7] \
    + [pop2(n) for n in range(2, 5)] \
    + [pop3(n) for n in range(2, 9)] \
    + []


def apply_rule(graph: mhg.MHGraph, rule: GraphNode) -> list[mhg.MHGraph]:
    """Apply the given reduction rule if possible.

    S : MHGraph -> R : list MHGraph
    fv : free Vertex of S

    S <= mhgraph
    - If no, then return mhgraph unchanged.
    - If yes, then store every way in which O is a subgraph of mhgraph.

    Run loop on "m"  m can fit O inside mhgraph.
    mO : MHGraph inside mhgraph
    mfv : Vertex of mO as well as mhgraph
    mReplace : MHGraph

    deg(fv, O) : this number should be preserved.
    Check deg(mfv, mhgraph) == deg(fv, O).
    - If no, then check the next "m".
    - If yes, then do the rewrite.
    mhgraph ->   mhgraph - mO + mReplace
    """
    is_subgraph: bool
    is_subgraph, sub_morphs = morph.subgraph_search(rule.graph,
                                                    graph,
                                                    return_all=True)
    if not is_subgraph:
        return [graph]

    sub_morphs = cast(Iterator[morph.Morphism], sub_morphs)
    for sub_morph in sub_morphs:
        mapped_free: Vertex
        mapped_free = sub_morph.translation[rule.free]
        if mhg.degree(mapped_free, graph) != mhg.degree(rule.free, rule.graph):
            continue

        mapped_parent: mhg.MHGraph
        mapped_parent = morph.graph_image(sub_morph, rule.graph)

        mapped_children: Iterator[mhg.MHGraph]
        mapped_children = (morph.graph_image(sub_morph, child.graph)
                           for child in rule.children)

        return [mhg.mhgraph(graph - mapped_parent + child) for child in mapped_children]
    return [graph]


@logger.catch
def make_tree(mhgraph: mhg.MHGraph, parent: Optional[GraphNode] = None) -> GraphNode:
    """Make a tree starting at mhgraph as root."""
    node = GraphNode(mhgraph, parent=parent or GraphNode(mhgraph))

    for rule in KNOWN_RULES:
        reduction: list[mhg.MHGraph] = apply_rule(mhgraph, rule)
        if reduction[0] != mhgraph:
            for child in reduction:
                make_tree(child, parent=node)
            return node
    return node


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
    g1: GraphNode = make_tree(g, None)
    print(g1)
    print(g1.leaves)

#!/usr/bin/env python3.9
"""Rewriting calculus for Criminal MHGraphs to make them human-readable."""

from typing import (AbstractSet, cast, Counter, Iterable, Iterator,
                    NamedTuple, Optional, TextIO, Tuple)

from colorama import Fore, init, Style  # type: ignore
from loguru import logger  # type: ignore
import typer

import graphsat.graph as graph
import graphsat.mhgraph as mhg
import graphsat.morphism as morph

import config
import dat_management as datm


# pylint: disable=invalid-name
app: typer.Typer = typer.Typer(add_completion=False)


class Term(NamedTuple):
    """A MHGraph, repr tuple."""
    mhg: Optional[mhg.MHGraph]
    rep: Tuple[str, ...]


def rw_subterm(pattern_subterm: Term, term: Term) -> Term:
    """Pattern match on a subterm of a term and rewrite it."""
    assert pattern_subterm.mhg is not None

    if term.mhg is None:
        return term

    has_mhg: bool
    has_mhg, subgraph_map = morph.subgraph_search(pattern_subterm.mhg, term.mhg, False)
    if not has_mhg:
        return term

    subgraph_map = cast(morph.Morphism, subgraph_map)

    mapped_subterm: mhg.MHGraph
    mapped_subterm = morph.graph_image(subgraph_map, pattern_subterm.mhg)

    reduced_mhg: Counter[AbstractSet[graph.Vertex]]
    reduced_mhg = term.mhg - mapped_subterm

    mhgraph: Optional[mhg.MHGraph] = mhg.mhgraph(reduced_mhg) if reduced_mhg else None
    new_vertices = ', '.join(map(str, map(subgraph_map.translation.get,
                                          mhg.vertices(pattern_subterm.mhg))))
    rep = term.rep + (f'{pattern_subterm.rep[0]}({new_vertices})' + Style.RESET_ALL,)
    return Term(mhgraph, rep)


def rw_pattern(mhgraph: mhg.MHGraph) -> Term:
    """Rewrite all the patterns in a mhgraph till no more rewrites are possible."""
    term: Term = Term(mhgraph, ())

    pentahedron = Term(mhg=mhg.mhgraph([[1, 2, 3], [1, 2, 4], [1, 2, 5],
                                        [1, 3, 4], [1, 3, 5],
                                        [1, 4, 5],
                                        [2, 3, 4], [2, 3, 5],
                                        [2, 4, 5],
                                        [3, 4, 5]]),
                       rep=(Style.BRIGHT + Fore.BLUE + 'Pent',))
    tetrahedron = Term(mhg=mhg.mhgraph([[1, 2, 3], [1, 2, 4], [1, 3, 4], [2, 3, 4]]),
                       rep=(Style.BRIGHT + Fore.GREEN + 'Tet',))
    three_tri = Term(mhg=mhg.mhgraph([[1, 2, 3], [1, 2, 4], [1, 3, 4]]),
                     rep=(Style.BRIGHT + Fore.YELLOW + '3-Tri',))
    triangle = Term(mhg=mhg.mhgraph([[1, 2], [1, 3], [2, 3]]),
                    rep=(Style.BRIGHT + Fore.RED + 'Tri',))

    subterms = [pentahedron, tetrahedron, three_tri, triangle]

    for subterm in subterms:
        while (rw_term := rw_subterm(subterm, term)) != term:
            term = rw_term
    return rw_term


def mhgraph_string(mhgraph: Optional[mhg.MHGraph]) -> str:
    """Convert to string."""
    if mhgraph is None:
        return ''
    if all(mul == 1 for mul in mhgraph.values()):
        return str(mhg.hgraph_from_mhgraph(mhgraph))
    return str(mhgraph)


def write_in_readable_form(criminals_iter: Iterable[mhg.MHGraph], writefile: TextIO) -> None:
    """Write criminals from criminals_iter in readable form to writefile."""
    for criminal in criminals_iter:
        term_of_criminal: Term = rw_pattern(criminal)
        mhg_str: str = mhgraph_string(term_of_criminal.mhg)
        total_rep = filter(None, term_of_criminal.rep + (mhg_str,))
        writefile.write(' + '.join(total_rep)
                        #+ '\t\t' + str(sorted((mhgraph.degree(v, c)
                        # for v in mhgraph.vertices(c)), reverse=True))
                        + '\n')


@app.command()
def write_criminals_reduced_to_human_readable(v: int = config.ARGDOCS['v'],
                                              emin: int = config.ARGDOCS['emin'],
                                              emax: int = config.ARGDOCS['emax'],
                                              mixed: str = config.ARGDOCS['mixed'],
                                              multi: str = config.ARGDOCS['multi']) -> None:
    """Write criminals_reduced.dat in human-readable form to criminals_reduced_human.dat"""
    cli_args: config.ArgsType = (v, emin, emax, mixed, multi)
    logger.add(config.files('readable_criminals_log', cli_args))

    criminals_reduced_dat: str
    criminals_reduced_dat = config.files('criminals_reduced', cli_args)

    criminals_reduced_human_dat: str
    criminals_reduced_human_dat = config.files('criminals_reduced_human', cli_args)

    criminals_reduced: Iterator[mhg.MHGraph]
    criminals_reduced = datm.read_dat(criminals_reduced_dat)

    with open(criminals_reduced_human_dat, 'w') as writefile:
        write_in_readable_form(criminals_reduced, writefile)
    config.print_end_message()

if __name__ == '__main__':
    init()
    app()

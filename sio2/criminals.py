#!/usr/bin/env python3.9
"""Functions for dealing with Criminals in the Hyper-Graph space.

A Criminal is a HGraph G such that:
* G is in U, and
* G is subgraph-minimal.

"""
# Imports from standard library.
import multiprocessing as mp
from typing import Any, Iterator, NewType, Sequence

# Imports from third-party packages.
from loguru import logger
import more_itertools as mit  # type: ignore
import tqdm  # type: ignore
import typer

# Local imports.
import graphsat.mhgraph as mhg
import graphsat.morphism as morph

import config
import dat_management as datm
import graph_rewrite as grw


# Initializing
# ------------
PROGRESS_BAR: Any = 0
app: typer.Typer = typer.Typer(add_completion=False)
Criminal = NewType('Criminal', mhg.MHGraph)


# Constants
# ---------
CRIMINALS_DEFAULT: list[Criminal]
CRIMINALS_DEFAULT = list(map(Criminal, datm.read_dat(config.CRIMINALS_DEFAULT_DAT)))


def has_unsat_subgraph(suspect: mhg.MHGraph, criminals_known: Sequence[Criminal]) -> bool:
    """Return True if one of the Criminals in criminals_known is a subgraph of suspect."""
    return any(morph.subgraph_search(c, suspect, return_all=False)[0]
               for c in criminals_known)


def write_criminals(criminals: Iterator[Criminal], cli_args: config.ArgsType) -> None:
    """Keep the ones we already had and then add in the ones we obtained."""
    criminals = mit.unique_everseen(criminals)
    criminals = filter(lambda c: c not in CRIMINALS_DEFAULT, criminals)

    criminals_dat: str = config.files('criminals', cli_args)
    datm.write_dat(criminals_dat, criminals)


def criminal_status(index_suspect: tuple[int, mhg.MHGraph]) -> tuple[str, mhg.MHGraph]:
    """Check if suspect is unsatisfiable and subgraph minimal. Return status.

    Possible statuses:
    - 'unsat-subgraph' if it is not subgraph-minimal,
    - 'sat' if it is satisfiable,
    - 'criminal' otherwise.
    """
    index: int
    suspect: mhg.MHGraph
    index, suspect = index_suspect
    PROGRESS_BAR.update()

    if has_unsat_subgraph(suspect, CRIMINALS_DEFAULT):
        logger.info(f'#{index + 1}: unsat-subgraph')
        return 'unsat-subgraph', suspect
    if grw.decompose(suspect):
        logger.info(f'#{index + 1}: sat')
        return 'sat', suspect
    logger.success(f'#{index + 1}: criminal')
    return 'criminal', suspect


def check_suspects(suspects: Iterator[mhg.MHGraph]) -> Iterator[Criminal]:
    """Run through SUSPECTS and report on status."""
    with mp.Pool() as pool:
        criminal_statuses = pool.imap_unordered(criminal_status,
                                                enumerate(suspects),
                                                chunksize=50)
        for status in criminal_statuses:
            if status[0] == 'criminal':
                yield Criminal(status[1])


def check_criminals(v: int = config.ARGDOCS['v'],
                    emin: int = config.ARGDOCS['emin'],
                    emax: int = config.ARGDOCS['emax'],
                    mixed: str = config.ARGDOCS['mixed'],
                    multi: str = config.ARGDOCS['multi']) -> None:
    """Check the criminal database.

    Desired output is a status of 'mhg-criminal' for all of them.
    This is supposed to run independent of check_suspects.
    """
    # We re-read criminals because they might have been over-written
    # by check_suspects()
    """criminals_dat: str = config.files('criminals', (v, emin, emax, mixed, multi))
    criminals = list(map(Criminal, datm.read_dat(criminals_dat)))  # pylint: disable=redefined-outer-name, invalid-name
    counts: Dict[str, int] = {'criminal': 0, 'unsat-sub': 0}

    progress = tqdm(enumerate(criminals),
                    total=len(criminals),
                    desc='check_criminals()',
                    disable=not config.PROGRESS_BAR,
                    miniters=1,
                    postfix=counts)
    for index, criminal in progress:
        # First step is to check if criminal is subgraph_minimal.
        if not subgraph_minimal(criminal, criminals[:index]):
            logger.info(f'Criminal #{index + 1} should be removed.')
            counts['unsat-sub'] += 1
            progress.set_postfix(counts)
            continue
        # Second step is to check if criminal is unsat.
        logger.trace(f'Satchecking criminal #{index + 1}.')
        if grw.decompose(criminal):
            logger.error(f'Criminal #{index + 1} is satisfiable.')
            break
        logger.trace(f'Criminal #{index + 1} is unsat and subgraph-minimal.')
        counts['criminal'] += 1
        progress.set_postfix(counts)
    """
    raise NotImplementedError


@app.command()
def check_suspects_and_write_results(v: int = config.ARGDOCS['v'],
                                     emin: int = config.ARGDOCS['emin'],
                                     emax: int = config.ARGDOCS['emax'],
                                     mixed: str = config.ARGDOCS['mixed'],
                                     multi: str = config.ARGDOCS['multi']) -> None:
    """Check suspects.dat and write results to criminals.dat."""
    cli_args: config.ArgsType = (v, emin, emax, mixed, multi)
    init_logs(cli_args)

    global PROGRESS_BAR
    PROGRESS_BAR = tqdm.tqdm(desc='criminals.py', leave=False)

    suspects_dat: str = config.files('suspects', cli_args)
    suspects: Iterator[mhg.MHGraph] = datm.read_dat(suspects_dat)

    criminals_new: Iterator[Criminal] = check_suspects(suspects)
    write_criminals(criminals_new, cli_args)
    config.print_end_message()


def init_logs(cli_args: config.ArgsType) -> None:
    """Initialize appropriate logs."""
    criminals_log: str = config.files('criminals_log', cli_args)
    logger.remove()
    logger.add(criminals_log, colorize=True, level=0, retention=1)
    logger.disable('graph_rewrite')
    logger.disable('graphsat')


if __name__ == '__main__':
    app()

#!/usr/bin/env python3.9
"""Global configurations for running all the files that compute criminals."""

# stdlib imports
import os
import socket
import time
from typing import Any

import tqdm  # type: ignore
import typer
from loguru import logger

# Constants
# =========

TESTING: bool = False  # If we are testing, then ignore the database file.
START_TIME: float = time.time()


# CLI setup
# =========

def argdoc(doc: str) -> Any:
    """Add documentation to a typer CLI argument."""
    return typer.Argument(..., help=doc)

ArgsType = tuple[int, int, int, str, str]

ARGDOCS = {'v': argdoc('(int) number of vertices'),
           'emin': argdoc('(int) lower end of edge range'),
           'emax': argdoc('(int) higher end of edge range'),
           'mixed': argdoc('(str) allow edges of all sizes "Mixed" or "Pure"'),
           'multi': argdoc('(str) allow multiplicities in edge "Multi" or "Uni"')}


# Folder and file names
# =====================

CRIMINALS_COMBINED: str = 'criminals_combined.dat'
CRIMINALS_COMBINED_HUMAN: str = 'criminals_combined_human.dat'
CRIMINALS_DEFAULT_DAT: str = 'criminals_default.dat'


def logfolder(cli_args: ArgsType) -> str:
    """Name of folder in which all files for a particular run are to be added."""
    v, emin, emax, mixed, multi = cli_args

    assert mixed in ['Mixed', 'Pure']
    assert multi in ['Multi', 'Uni']

    return f'{v}_{emin}_{emax}_{mixed}_{multi}'


def files(name: str, cli_args: ArgsType) -> str:
    """Return filenames for a particular run."""
    basename = name + '.dat'
    return os.path.join(logfolder(cli_args), basename)


# Progress and Logs
# =================


def print_end_message() -> None:
    """Print helpful messages at the end of running this script."""
    time_elapsed: float = time.time() - START_TIME
    logger.success(f"Total time taken = {round(time_elapsed, 2)}s")


def progress_bar() -> Any:
    """Initialize a progress bar.

    If not running this on my personal computer, then turn off tqdm
    progress bars.
    """
    return tqdm.tqdm(disable=socket.gethostname() != 'vk76')

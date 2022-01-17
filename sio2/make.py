#!/usr/bin/env python3.9
"""Run commands that perform the calculations."""
import os
from pathlib import Path
import shutil
import subprocess
from typing import Optional, Set

from loguru import logger
import typer

import graphsat.cnf as cnf
import graphsat.cnf_simplify as csimp
import graphsat.graph_collapse as gcollapse
import graphsat.mhgraph as mhg
import graphsat.operations as op

import config

import combine_criminals as combine
import criminals as crim
import reduce_by_rules as rbr
import readable_criminals as readable


USE_CONDA: bool = False
app: typer.Typer = typer.Typer(add_completion=False)


# pylint: disable=invalid-name


def simplify_graph_rewrite_output() -> None:
    """s,(23 ∨ 25, 34, 45) ∪ s,(25 ∨ 23, 34, 45)
       ∪ s,(34 ∨ 23, 25, 45) ∪ s,(45 ∨ 23, 25, 34)
       ∪ s,(23, 25 ∨ 34, 45) ∪ s,(23, 34 ∨ 25, 45) ∪ s,(23, 45 ∨ 25, 34)
       """
    g1: mhg.MHGraph = mhg.mhgraph([[2, 3]])
    g2: mhg.MHGraph = mhg.mhgraph([[2, 5], [3, 4], [4, 5]])

    g3: mhg.MHGraph = mhg.mhgraph([[2, 5]])
    g4: mhg.MHGraph = mhg.mhgraph([[2, 3], [3, 4], [4, 5]])

    g5: mhg.MHGraph = mhg.mhgraph([[3, 4]])
    g6: mhg.MHGraph = mhg.mhgraph([[2, 3], [2, 5], [4, 5]])

    g7: mhg.MHGraph = mhg.mhgraph([[4, 5]])
    g8: mhg.MHGraph = mhg.mhgraph([[2, 3], [2, 5], [3, 4]])

    g9: mhg.MHGraph = mhg.mhgraph([[2, 3], [2, 5]])
    g10: mhg.MHGraph = mhg.mhgraph([[3, 4], [4, 5]])

    g11: mhg.MHGraph = mhg.mhgraph([[2, 3], [3, 4]])
    g12: mhg.MHGraph = mhg.mhgraph([[2, 5], [4, 5]])

    g13: mhg.MHGraph = mhg.mhgraph([[2, 3], [4, 5]])
    g14: mhg.MHGraph = mhg.mhgraph([[2, 5], [3, 4]])

    cnfs: Set[cnf.Cnf]
    cnfs = op.graph_or(g1, g2) | op.graph_or(g3, g4) | op.graph_or(g5, g6) | op.graph_or(g7, g8) \
        | op.graph_or(g9, g10) | op.graph_or(g11, g12) | op.graph_or(g13, g14)
    gcollapse.print_grouping_table(set(map(csimp.reduce_cnf, cnfs)))


@app.command()
def folder(v: int = config.ARGDOCS['v'],
           emin: int = config.ARGDOCS['emin'],
           emax: int = config.ARGDOCS['emax'],
           mixed: str = config.ARGDOCS['mixed'],
           multi: str = config.ARGDOCS['multi']) -> Optional[str]:
    """Make parametrized folder V_EMIN_EMAX_{a}_{b}.

    Folder is for storing log files. {a} can be Mixed/Pure. {b} can
    be Multi/Uni.  Returns the name of the logfolder.
    """
    logfolder: str = config.logfolder((v, emin, emax, mixed, multi))
    try:
        os.mkdir(logfolder)
        return logfolder
    except FileExistsError:
        return None


@app.command()
def suspects(v: int = config.ARGDOCS['v'],
             emin: int = config.ARGDOCS['emin'],
             emax: int = config.ARGDOCS['emax'],
             mixed: str = config.ARGDOCS['mixed'],
             multi: str = config.ARGDOCS['multi']) -> None:
    """Write suspects to suspects.dat in the appropriate folder."""
    cli_args: config.ArgsType = (v, emin, emax, mixed, multi)

    if USE_CONDA:
        conda_env_path: Path = Path('~/.miniconda3/envs/sage')
        command: str = f'conda run -p {conda_env_path} suspects.sage'
    else:
        command = f'sage suspects.sage'
    suspects_file: str = config.files('suspects', cli_args)
    logger.info(f'Running "{command}"')
    subprocess.run(f'{command} {v} {emin} {emax} {mixed} {multi}',
                   check=True, shell=True)
    subprocess.run(f'wc -l {suspects_file}', check=True, shell=True)


@app.command()
def criminals(v: int = config.ARGDOCS['v'],
              emin: int = config.ARGDOCS['emin'],
              emax: int = config.ARGDOCS['emax'],
              mixed: str = config.ARGDOCS['mixed'],
              multi: str = config.ARGDOCS['multi']) -> None:
    """Check suspects.dat using graph-rewrite.

    Write results in criminals.dat."""
    cli_args: config.ArgsType = (v, emin, emax, mixed, multi)
    criminals_file: str = config.files('criminals', cli_args)
    crim.check_suspects_and_write_results(*cli_args)
    print()
    subprocess.run(f'wc -l {criminals_file}', check=True, shell=True)


@app.command()
def reduce_criminals(v: int = config.ARGDOCS['v'],
                     emin: int = config.ARGDOCS['emin'],
                     emax: int = config.ARGDOCS['emax'],
                     mixed: str = config.ARGDOCS['mixed'],
                     multi: str = config.ARGDOCS['multi']) -> None:
    """Apply reduction rules to criminals.dat and write to criminals_reduced.dat."""
    cli_args: config.ArgsType = (v, emin, emax, mixed, multi)
    rbr.write_reduced_criminals(*cli_args)
    criminals_reduced_file: str = config.files('criminals_reduced', cli_args)
    print()
    subprocess.run(f'wc -l {criminals_reduced_file}', check=True, shell=True)


@app.command()
def readable_criminals(v: int = config.ARGDOCS['v'],
                       emin: int = config.ARGDOCS['emin'],
                       emax: int = config.ARGDOCS['emax'],
                       mixed: str = config.ARGDOCS['mixed'],
                       multi: str = config.ARGDOCS['multi']) -> None:
    """Write criminals_reduced.dat in human-readable form to criminals_reduced_human.dat"""
    cli_args: config.ArgsType = (v, emin, emax, mixed, multi)
    readable.write_criminals_reduced_to_human_readable(*cli_args)
    criminals_readable_file: str = config.files('criminals_reduced_human', cli_args)
    subprocess.run(f'wc -l {criminals_readable_file}', check=True, shell=True)



@app.command()
def combine_criminals() -> None:
    """Combine all criminals into one dat file."""
    combine.combine_criminals()
    subprocess.run('wc -l criminals_default.dat', check=True, shell=True)
    subprocess.run('wc -l criminals_combined.dat', check=True, shell=True)
    subprocess.run('wc -l criminals_combined_human.dat', check=True, shell=True)


@app.command()
def clean(v: int = config.ARGDOCS['v'],
          emin: int = config.ARGDOCS['emin'],
          emax: int = config.ARGDOCS['emax'],
          mixed: str = config.ARGDOCS['mixed'],
          multi: str = config.ARGDOCS['multi']) -> None:
    """Remove directory."""
    try:
        logfolder: str = config.logfolder((v, emin, emax, mixed, multi))
        shutil.rmtree(logfolder)
        print(f'Deleted {logfolder}')
    except FileNotFoundError:
        pass


@app.command()
def all(v: int = config.ARGDOCS['v'],
        emin: int = config.ARGDOCS['emin'],
        emax: int = config.ARGDOCS['emax'],
        mixed: str = config.ARGDOCS['mixed'],
        multi: str = config.ARGDOCS['multi']) -> None:
    """Perform a list of actions in sequence."""
    cli_args: config.ArgsType = v, emin, emax, mixed, multi

    # Run all these commands in order
    #clean(*cli_args)
    folder(*cli_args)
    suspects(*cli_args)
    #criminals(*cli_args)
    #reduce_criminals(*cli_args)
    #readable_criminals(*cli_args)
    # Run independent of cli_args.
    #combine_criminals()


if __name__ == '__main__':
    app()

#!/usr/bin/env python3.9
"""Combine criminals_reduced.dat from all the subfolders into one.

TODO: Currently there is no guarantee that every MHGraph in the
combined list is subgraph minimal. Will need to add a check for this.

"""
import os

import more_itertools as mit
import typer

import graphsat.morphism as morph

import config
import dat_management as datm
import readable_criminals as readable


# pylint: disable=invalid-name
app = typer.Typer(add_completion=False)
IGNORE: list[str] = ['.mypy_cache', '__pycache__']


@app.command()
def combine_criminals() -> None:
    """Combine all criminals into one dat file."""
    dirs = list(filter(os.path.isdir, os.listdir()))
    dirs = list(filter(lambda d: d not in IGNORE, dirs))

    criminal_files: list[str] = [config.CRIMINALS_DEFAULT_DAT]
    criminal_files.extend([os.path.join(d, 'criminals_reduced.dat') for d in dirs])

    criminal_list = mit.flatten(map(datm.read_dat, criminal_files))
    criminal_list_nodup = list(morph.unique_upto_isom(criminal_list))

    with open(config.CRIMINALS_COMBINED, 'w') as writefile:
        writefile.write('\n'.join(map(str, criminal_list_nodup)))
        writefile.write('\n')

    with open(config.CRIMINALS_COMBINED_HUMAN, 'w') as writefile:
        readable.write_in_readable_form(criminal_list_nodup, writefile)
    config.print_end_message()

if __name__ == '__main__':
    app()

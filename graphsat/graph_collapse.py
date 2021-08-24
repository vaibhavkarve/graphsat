#!/usr/bin/env python3.9
"""Functions for collapsing a set of Cnfs into compact graphs representation."""

import collections
import itertools as it
from typing import Any, DefaultDict

from tabulate import tabulate
from tqdm import tqdm  # type: ignore

import graphsat.cnf as cnf
import graphsat.mhgraph as mhg
import graphsat.operations as op
import graphsat.sat as sat


_TRUE_FALSE: dict[cnf.Cnf, str]
_TRUE_FALSE = {cnf._TRUE_CNF: 'TRUE_Graph', cnf._FALSE_CNF: 'FALSE_Graph'}


def is_complete_cnf_set(cnf_set: set[cnf.Cnf], graph: mhg.MHGraph) -> bool:
    """Check if a set of Cnfs is the complete set on the given MHGraph."""
    for x in sat.cnfs_from_mhgraph(graph):
        if not x in cnf_set:
            return False
    return True


def group_trivial_cnf(cnf_set: set[cnf.Cnf]) -> dict[str, set[cnf.Cnf]]:
    """Put trivial Cnfs in a printable dict."""
    return  {_TRUE_FALSE[x] : {x} for x in _TRUE_FALSE if x in cnf_set}


def group_set_cnf_by_mhgraph(cnf_set: set[cnf.Cnf]) -> DefaultDict[mhg.MHGraph, set[Any]]:
    """Group non-trivial Cnfs by mhgraphs.

    We will use itertools.groupby for the grouping with sat.mhgraph_from_cnf as the
    key.  True/False Cnfs in the set will raise ValueError.

    """
    group: DefaultDict[mhg.MHGraph, set[cnf.Cnf]]
    group = collections.defaultdict(set)

    for key, value in it.groupby(cnf_set, sat.mhgraph_from_cnf):
        group[key] |= set(value)
    return group


def create_grouping(cnf_set: set[cnf.Cnf]) -> dict[Any, Any]:
    """Group cnfs in the set according to their MHGraph supports.
    """
    group_trivial: dict[str, set[cnf.Cnf]]
    group_trivial = group_trivial_cnf(cnf_set)

    group_nontrivial: DefaultDict[mhg.MHGraph, set[Any]]
    group_nontrivial = group_set_cnf_by_mhgraph(cnf_set - set(_TRUE_FALSE.keys()))

    for key, value in group_nontrivial.items():
        if is_complete_cnf_set(value, key):
            group_nontrivial[key] = {'Complete'}

    group_combined: dict[Any, Any]
    group_combined = group_trivial | group_nontrivial  # type: ignore
    return group_combined



def print_grouping_table(cnf_set: set[cnf.Cnf]) -> None:
    """Print table after grouping.

    Indicate complete sets by the string 'Complete'.

    """
    group_combined: dict[Any, Any] = create_grouping(cnf_set)
    print('\n', tabulate(group_combined,
                         headers=list(group_combined.keys()),
                         showindex=True))


if __name__ == '__main__':
    g1: mhg.MHGraph = mhg.mhgraph([[2, 3]])
    g2: mhg.MHGraph = mhg.mhgraph([[3, 4], [4, 5]])
    g3: mhg.MHGraph = mhg.mhgraph([[3, 4]])
    g4: mhg.MHGraph = mhg.mhgraph([[2, 3], [4, 5]])
    g5: mhg.MHGraph = mhg.mhgraph([[4, 5]])
    g6: mhg.MHGraph = mhg.mhgraph([[2, 3], [3, 4]])

    cnfs: set[cnf.Cnf]
    cnfs = op.graph_or(g1, g2) | op.graph_or(g3, g4) | op.graph_or(g5, g6)
    print_grouping_table(cnfs)

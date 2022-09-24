#!/usr/bin/env python3.8
"""Functions for collapsing a set of Cnfs into compact graphs representation."""

import itertools as it
from collections import defaultdict
from typing import Any, Iterator, Literal, TypeAlias

from tabulate import tabulate
from graphsat import translation

import graphsat.mhgraph as mhg
import graphsat.operations as op
from normal_form import cnf, sat
from graphsat.translation import cnfs_from_mhgraph

TF_Graph: TypeAlias = Literal["TRUE_Graph", "FALSE_Graph"]
_TRUE_FALSE: dict[cnf.Cnf, TF_Graph]
_TRUE_FALSE = {cnf.TRUE_CNF: "TRUE_Graph", cnf.FALSE_CNF: "FALSE_Graph"}


def is_complete_cnf_set(cnf_set: set[cnf.Cnf], graph: mhg.MHGraph) -> bool:
    """Check if a set of Cnfs is the complete set on the given MHGraph."""
    return all(x in cnf_set for x in cnfs_from_mhgraph(graph))


def group_trivial_cnf(cnf_set: set[cnf.Cnf]) -> dict[TF_Graph, set[cnf.Cnf]]:
    """Put trivial Cnfs in a printable dict."""
    return  {str_value : {cnf_key} for cnf_key, str_value in _TRUE_FALSE.items()
             if cnf_key in cnf_set}


def group_set_cnf_by_mhgraph(cnf_set: set[cnf.Cnf]) -> dict[mhg.MHGraph, set[cnf.Cnf]]:
    """Group non-trivial Cnfs by mhgraphs.

    We will use itertools.groupby for the grouping with sat.mhgraph_from_cnf as the
    key.  True/False Cnfs in the set will raise ValueError.

    """
    group: defaultdict[mhg.MHGraph, set[cnf.Cnf]] = defaultdict(set)

    key: mhg.MHGraph
    value: Iterator[cnf.Cnf]
    for key, value in it.groupby(cnf_set, translation.mhgraph_from_cnf):
        group[key] |= set(value)
    return group


def create_grouping(cnf_set: set[cnf.Cnf]) \
        -> dict[mhg.MHGraph | TF_Graph, set[cnf.Cnf] | Literal["Complete"]]:
    """Group Cnfs in the set according to their MHGraph supports.

    We return a dictionary of MHGraph -> set[Cnf] type.
    - Every Cnf gets assinged to a key (MHGraph) which supports it.
    - The True and False Cnfs gets assigned to the literal strings "TRUE_Graph"
      and "FALSE_Graph" respectively.
    - If a MHGraph supports all possible underlying Cnfs, instead of listing them individually,
      we replace the set with the literal string "Complete".
    """
    group_trivial: dict[TF_Graph, set[cnf.Cnf]]
    group_trivial = group_trivial_cnf(cnf_set)

    group_nontrivial: dict[mhg.MHGraph, set[cnf.Cnf]]
    group_nontrivial = group_set_cnf_by_mhgraph(cnf_set - set(_TRUE_FALSE.keys()))

    group_combined: dict[mhg.MHGraph | TF_Graph, set[cnf.Cnf] | Literal["Complete"]] = {}
    for key, value in group_nontrivial.items():
        if is_complete_cnf_set(value, key):
            group_combined[key] = 'Complete'
        else:
            group_combined[key] = value

    group_combined = group_combined | group_trivial  # type: ignore
    return group_combined



def print_grouping_table(cnf_set: set[cnf.Cnf]) -> None:
    """Print table after grouping.

    Indicate complete sets by the string 'Complete'.

    """
    group_combined: dict[Any, Any] = create_grouping(cnf_set)
    print('\n', tabulate(group_combined,
                         headers=list(group_combined.keys()),
                         showindex=True))


if __name__ == '__main__':  # pragma: no cover
    g1: mhg.MHGraph = mhg.mhgraph([[2, 3, 4]])
    g2: mhg.MHGraph = mhg.mhgraph([[2, 3, 5]])
    g3: mhg.MHGraph = mhg.mhgraph([[2, 3, 4]])
    g4: mhg.MHGraph = mhg.mhgraph([[2, 3, 5]])
    g5: mhg.MHGraph = mhg.mhgraph([[2, 3, 4]])
    g6: mhg.MHGraph = mhg.mhgraph([[2, 3, 5]])

    cnfs: set[cnf.Cnf]
    cnfs = op.graph_or(g1, g2) | op.graph_or(g3, g4) | op.graph_or(g5, g6)
    print_grouping_table(cnfs)

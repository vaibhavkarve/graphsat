#!/usr/bin/env python3.8


from normal_form.cnf import FALSE_CNF, TRUE_CNF, Cnf, cnf
from graphsat.graph_collapse import (group_set_cnf_by_mhgraph,
                                     group_trivial_cnf, is_complete_cnf_set)
from graphsat.mhgraph import MHGraph, mhgraph


def test_is_complete_cnf_set() -> None:
    assert not is_complete_cnf_set(set(), mhgraph([[1]]))
    assert not is_complete_cnf_set({cnf([[1]])}, mhgraph([[1]]))
    assert is_complete_cnf_set({cnf([[1]]), cnf([[-1]])}, mhgraph([[1]]))
    assert is_complete_cnf_set({cnf([[1, 2]]), cnf([[1, -2]]),
                                cnf([[-1, 2]]), cnf([[-1, -2]])},
                               mhgraph([[1, 2]]))


def test_group_trivial_cnf() -> None:
    assert not group_trivial_cnf(set())
    assert group_trivial_cnf({TRUE_CNF}) == {'TRUE_Graph': {TRUE_CNF}}
    assert group_trivial_cnf({FALSE_CNF}) == {'FALSE_Graph': {FALSE_CNF}}
    assert group_trivial_cnf({TRUE_CNF, FALSE_CNF}) \
        == {'TRUE_Graph' : {TRUE_CNF}, 'FALSE_Graph': {FALSE_CNF}}
    assert group_trivial_cnf({TRUE_CNF, cnf([[1]])}) \
        == group_trivial_cnf({TRUE_CNF})


def test_group_set_cnf_by_mhgraph() -> None:
    s1: set[Cnf] = {cnf([[1, 2]]), cnf([[-1, -2]])}
    g1: MHGraph = mhgraph([[1, 2]])

    s2: set[Cnf] = {cnf([[1, 2, 3]]), cnf([[-1, -2, -3]])}
    g2: MHGraph = mhgraph([[1, 2, 3]])

    assert group_set_cnf_by_mhgraph(set()) == {}
    assert group_set_cnf_by_mhgraph(s1) == {g1 : s1}
    assert group_set_cnf_by_mhgraph(s2) == {g2 : s2}
    assert group_set_cnf_by_mhgraph(s1|s2) == {g1: s1, g2: s2}

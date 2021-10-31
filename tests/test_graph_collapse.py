#!/usr/bin/env python3.8

import pytest

from graphsat.graph_collapse import *


def test_is_complete_cnf_set() -> None:
    assert not is_complete_cnf_set(set(), mhg.mhgraph([[1]]))
    assert not is_complete_cnf_set({cnf.cnf([[1]])}, mhg.mhgraph([[1]]))
    assert is_complete_cnf_set({cnf.cnf([[1]]), cnf.cnf([[-1]])}, mhg.mhgraph([[1]]))
    assert is_complete_cnf_set({cnf.cnf([[1, 2]]), cnf.cnf([[1, -2]]),
                                cnf.cnf([[-1, 2]]), cnf.cnf([[-1, -2]])},
                               mhg.mhgraph([[1, 2]]))


def test_group_trivial_cnf() -> None:
    assert not group_trivial_cnf(set())
    assert group_trivial_cnf({cnf._TRUE_CNF}) == {'TRUE_Graph': {cnf._TRUE_CNF}}
    assert group_trivial_cnf({cnf._FALSE_CNF}) == {'FALSE_Graph': {cnf._FALSE_CNF}}
    assert group_trivial_cnf({cnf._TRUE_CNF, cnf._FALSE_CNF}) \
        == {'TRUE_Graph' : {cnf._TRUE_CNF}, 'FALSE_Graph': {cnf._FALSE_CNF}}
    assert group_trivial_cnf({cnf._TRUE_CNF, cnf.cnf([[1]])}) \
        == group_trivial_cnf({cnf._TRUE_CNF})


def test_group_set_cnf_by_mhgraph() -> None:
    s1: Set[cnf.Cnf] = {cnf.cnf([[1, 2]]), cnf.cnf([[-1, -2]])}
    g1: mhg.MHGraph = mhg.mhgraph([[1, 2]])

    s2: Set[cnf.Cnf] = {cnf.cnf([[1, 2, 3]]), cnf.cnf([[-1, -2, -3]])}
    g2: mhg.MHGraph = mhg.mhgraph([[1, 2, 3]])

    assert group_set_cnf_by_mhgraph(set()) == {}
    assert group_set_cnf_by_mhgraph(s1) == {g1 : s1}
    assert group_set_cnf_by_mhgraph(s2) == {g2 : s2}
    assert group_set_cnf_by_mhgraph(s1|s2) == {g1: s1, g2: s2}

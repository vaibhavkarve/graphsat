#!/usr/bin/env python3.8
"""Tests for cnf_simplify.py."""

from graphsat.cnf import cnf, clause, absolute_value, lit, Clause, Cnf
from graphsat.mhgraph import hedge
from graphsat.cnf_simplify import (differing_lits,
                                   equivalent_smaller_clause, hedge_of_clause,
                                   reduce_cnf)


def test_hedge_of_clause() -> None:
    assert hedge_of_clause(clause([1, -2, -3])) == hedge([1, 2, 3])


def test_differing_lits() -> None:
    c1: Clause = clause([1, 2, -3])
    c2: Clause = clause([-1, -2, -3])
    assert not differing_lits(c1, c1)
    assert not differing_lits(c2, c2)
    assert differing_lits(c1, c2) == {lit(1), lit(2), lit(-1), lit(-2)}
    assert differing_lits(c1, c2) == differing_lits(c2, c1)


def test_equivalent_smaller_clause() -> None:
    c1: Clause = clause([1, 2, -3])
    c2: Clause = clause([1, 2, 3])
    assert equivalent_smaller_clause(c1, c2) == clause([1, 2])


def test_reduce_cnf() -> None:
    x: Cnf = cnf([[1, 2, -3], [1, 2, 3], [-1, -2, 3], [4, 5]])
    x_red: Cnf = cnf([[1, 2], [-1, -2, 3], [4, 5]])
    assert reduce_cnf(x) == x_red

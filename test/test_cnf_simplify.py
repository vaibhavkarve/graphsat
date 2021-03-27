#!/usr/bin/env python3.9
"""Tests for cnf.simplify.py."""

import pytest
from cnf_simplify import *


def test_hedge_of_clause() -> None:
    assert hedge_of_clause(cnf.clause([1, -2, -3])) == mhg.hedge([1, 2, 3])


def test_differing_lits() -> None:
    c1: cnf.Clause = cnf.clause([1, 2, -3])
    c2: cnf.Clause = cnf.clause([-1, -2, -3])
    assert not differing_lits(c1, c1)
    assert not differing_lits(c2, c2)
    assert differing_lits(c1, c2) == {1, 2, -1, -2}
    assert differing_lits(c1, c2) == differing_lits(c2, c1)


def test_equivalent_smaller_clause() -> None:
    c1: cnf.Clause = cnf.clause([1, 2, -3])
    c2: cnf.Clause = cnf.clause([1, 2, 3])
    assert equivalent_smaller_clause(c1, c2) == cnf.clause([1, 2])


def test_reduce_cnf() -> None:
    x: cnf.Cnf = cnf.cnf([[1, 2, -3], [1, 2, 3], [-1, -2, 3], [4, 5]])
    x_red: cnf.Cnf = cnf.cnf([[1, 2], [-1, -2, 3], [4, 5]])
    assert reduce_cnf(x) == x_red

#!/usr/bin/env python3.8

import pytest

from graphsat.cnf import cnf, lit, clause
from graphsat.prop import (clause_and_literal, clause_or_literal,
                           literal_and_literal, literal_or_literal)

pytestmark = pytest.mark.skip('\n  All tests still WIP')

def test_literal_and_literal() -> None:
    assert literal_and_literal(lit(1), lit(-2)) == cnf([[1], [-2]])

def test_clause_and_literal() -> None:
    assert clause_and_literal(clause([1, 2]), lit(3)) == cnf([[1, 2], [3]])

def test_clause_and_clause() -> None:
    raise NotImplementedError

def test_cnf_and_lieral() -> None:
    raise NotImplementedError

def test_cnf_and_clause() -> None:
    raise NotImplementedError

def test_cnf_and_cnf() -> None:
    raise NotImplementedError

def test_literal_or_literal() -> None:
    assert literal_or_literal(lit(1), lit(-2)) == clause([1, -2])

def test_clause_or_literal() -> None:
    assert clause_or_literal(clause([1, 2]), lit(3)) == cnf([[1, 2], [3]])

def test_clause_or_clause() -> None:
    raise NotImplementedError

def test_cnf_or_lieral() -> None:
    raise NotImplementedError

def test_cnf_or_clause() -> None:
    raise NotImplementedError

def test_cnf_or_cnf() -> None:
    raise NotImplementedError

def test_neg_clause() -> None:
    raise NotImplementedError

def test_neg_cnf() -> None:
    raise NotImplementedError

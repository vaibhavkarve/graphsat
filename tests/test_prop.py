#!/usr/bin/env python3.8

import pytest

from graphsat.prop import *

pytestmark = pytest.mark.skip('\n  All tests still WIP')

def test_literal_and_literal():
    assert literal_and_literal(1, -2) == cnf.cnf([[1], [-2]])

def test_clause_and_literal():
    assert clause_and_literal(cnf.clause([1, 2]), 3) == cnf.cnf([[1, 2], [3]])

def test_clause_and_clause():
    raise NotImplementedError

def test_cnf_and_lieral():
    raise NotImplementedError

def test_cnf_and_clause():
    raise NotImplementedError

def test_cnf_and_cnf():
    raise NotImplementedError

def test_literal_or_literal():
    assert literal_or_literal(1, -2) == cnf.cnf([[1], [-2]])

def test_clause_or_literal():
    assert clause_or_literal(cnf.clause([1, 2]), 3) == cnf.cnf([[1, 2], [3]])

def test_clause_or_clause():
    raise NotImplementedError

def test_cnf_or_lieral():
    raise NotImplementedError

def test_cnf_or_clause():
    raise NotImplementedError

def test_cnf_or_cnf():
    raise NotImplementedError

def test_neg_clause():
    raise NotImplementedError

def test_neg_cnf():
    raise NotImplementedError

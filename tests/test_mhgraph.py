#! /usr/bin/env python3.8

import pytest
from context import graphsat
from graphsat import mhgraph
from mhgraph import *


class TestPreMHGraph(object):
    def test__hash__(self):
        assert hash(MHGraphType([(1, 2), (2, 3), (2, 3)])) \
            == hash(MHGraphType(counter({(1, 2): 1, (2, 3): 2})))

    def test__repr__(self):
        assert repr(mhgraph([[1, 2], [2, 3], [3, 2]])) in \
        ['(1, 2)¹,(2, 3)²', '(1, 2)¹,(3, 2)²', '(2, 1)¹,(2, 3)²', '(2, 1)¹,(3, 2)²']


def test_hedge():
    assert hedge([1]) == {1}
    assert hedge([1, 2]) == {1, 2}
    assert hedge([1, 2, 1]) == {1, 2}

    with pytest.raises(ValueError):
        hedge([])
    with pytest.raises(ValueError):
        hedge([0])
    with pytest.raises(ValueError):
        hedge([2, -1])


def test_hgraph():
    assert hgraph([[1]]) == {frozenset({1})}
    assert hgraph([[1, 2]]) == {frozenset({1, 2})}
    assert hgraph([[1, 2], [2, 1]]) == {frozenset({1, 2})}

    assert hgraph(counter({(1,)})) == {frozenset({1})}
    assert hgraph(counter({(1, 2)})) == {frozenset({1, 2})}
    assert hgraph(counter({(1, 2)})) == {frozenset({1, 2})}

    # Test for idempotence
    assert hgraph(hgraph([[1, 2], [2, 1], [3]])) == hgraph([[1, 2], [2, 1], [3]])

    with pytest.raises(ValueError):
        hgraph([[]])
    with pytest.raises(ValueError):
        hgraph([[0]])
    with pytest.raises(ValueError):
        hgraph([[-1]])


def test_mhgraph():
    assert mhgraph([[1]]) == {frozenset({1}): 1}
    assert mhgraph([[1, 2]]) == {frozenset({1, 2}) : 1}
    assert mhgraph([[1, 2], [2, 1]]) == {frozenset({1, 2}) : 2}

    assert mhgraph(counter({(1,): 1})) == {frozenset({1}): 1}
    assert mhgraph(counter({(1, 2): 1})) == {frozenset({1, 2}) : 1}
    assert mhgraph(counter({(1, 2): 2})) == {frozenset({1, 2}) : 2}

    # Test for idempotence
    assert mhgraph(mhgraph([[1, 2], [2, 1], [3]])) == mhgraph([[1, 2], [2, 1], [3]])

    with pytest.raises(ValueError):
        mhgraph([[]])
    with pytest.raises(ValueError):
        mhgraph([[0]])
    with pytest.raises(ValueError):
        mhgraph([[-1]])


def test_vertices():
    assert vertices(mhgraph([[1,2,3], [4], [1, 2]])) == {1, 2, 3, 4}


def test_degree():
    assert degree(2, mhgraph([[1, 2], [3, 4, 2], [1, 2]])) == 3
    assert degree(1, mhgraph([[1, 2], [3, 4, 2], [1, 2]])) == 2
    assert degree(4, mhgraph([[1, 2], [3, 4, 2], [1, 2]])) == 1
    assert degree(5, mhgraph([[1, 2], [3, 4, 2], [1, 2]])) == 0

def test_graph_union():
    assert graph_union(mhgraph([[1, 2], [3]]), mhgraph([[1, 11]])) ==  mhgraph([[1, 2], [3], [1, 11]])

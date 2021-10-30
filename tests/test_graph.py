#! /usr/bin/env python3.8

import pytest
from graphsat.graph import *


def test_pregraph__repr__():
        assert repr(graph([[1, 2], [2, 3], [3, 2]])) == '(1,2),(2,3)'


def test_vertex():
    assert vertex(1) == 1
    assert vertex(22) == 22

    # Test for idempotence.
    assert vertex(vertex(1)) == vertex(1)

    with pytest.raises(ValueError):
        vertex(0)
    with pytest.raises(ValueError):
        vertex(-1)


def test_edge():
    assert edge([1]) == {1}
    assert edge([1, 2]) == {1, 2}
    assert edge([2, 1]) == {1, 2}

    with pytest.raises(ValueError):
        edge([])
    with pytest.raises(ValueError):
        edge([0])
    with pytest.raises(ValueError):
        edge([2, -1])


def test_graph():
    assert graph([[1]]) == {frozenset({1})}
    assert graph([[1, 2]]) == {frozenset({1, 2})}
    assert graph([[1, 2], [2, 1]]) == {frozenset({1, 2})}

    # Test for idempotence
    assert graph(graph([[1, 2], [2, 1], [3]])) == graph([[1, 2], [2, 1], [3]])

    # Check that single-vertex-edges are disjoint from vertex-pair-edges
    assert graph([[1, 2], [3, 4]]) == {frozenset({1, 2}), frozenset({3, 4})}
    assert graph([[1], [3]]) == {frozenset({1}), frozenset({3})}
    assert graph([[1, 2], [3]]) == {frozenset({1, 2}), frozenset({3})}
    assert graph([[1, 2], [1]]) == {frozenset({1, 2}), frozenset({1})}


    with pytest.raises(ValueError):
        graph([[]])
    with pytest.raises(ValueError):
        graph([[0]])
    with pytest.raises(ValueError):
        graph([[-1]])


def test_vertices():
    assert vertices(graph([[1, 2], [4], [1, 3]])) == {1, 2, 3, 4}

#!/usr/bin/env python3.9
"""Unit tests for `hyperbolic_guess.py`"""
import pytest
from hyperbolic_guess import *


def test_hyperbolic_filter():
    g: mhg.MHGraph = mhg.mhgraph([[1, 2, 3], [1, 2, 4], [1, 3, 4], [2, 3, 4]])
    vertices: frozenset[graph.Vertex] = {1, 2, 3, 4}

    x1: cnf.Cnf = cnf.cnf([[1, 2, 3], [1, 2, 4], [1, 3, 4], [2, 3, 4]])
    x2: cnf.Cnf = cnf.cnf([[1, 2, 3], [-1, 2, 4], [1, 3, 4], [2, 3, 4]])
    x3: cnf.Cnf = cnf.cnf([[1, 2, -3], [-1, -2, -4], [1, -3, 4], [2, 3, -4]])
    x4: cnf.Cnf = cnf.cnf([[-1, -2, -3], [-1, -2, -4], [-1, -3, -4], [-2, -3, -4]])

    assert not hyperbolic_filter(vertices, x1)
    assert not hyperbolic_filter(vertices, x2)
    assert hyperbolic_filter(vertices, x3)
    assert not hyperbolic_filter(vertices, x4)


def test_generate_hyperbolic_cnfs():
    g: mhg.MHGraph = mhg.mhgraph([[1]])
    assert len(list(generate_hyperbolic_cnfs(g))) == 2

    g: mhg.MHGraph = mhg.mhgraph([[1, 2]])
    assert len(list(generate_hyperbolic_cnfs(g))) == 4

    g: mhg.MHGraph = mhg.mhgraph([[1, 2]]*2)
    assert len(list(generate_hyperbolic_cnfs(g))) == 2

    g: mhg.MHGraph = mhg.mhgraph([[1, 2]]*3)
    assert len(list(generate_hyperbolic_cnfs(g))) == 4

    g: mhg.MHGraph = mhg.mhgraph([[1, 2]]*4)
    assert len(list(generate_hyperbolic_cnfs(g))) == 1

    g: mhg.MHGraph = mhg.mhgraph([[1, 2]])
    assert len(list(generate_hyperbolic_cnfs(g))) == 4

    g: mhg.MHGraph = mhg.mhgraph([[1, 2, 3]])
    assert len(list(generate_hyperbolic_cnfs(g))) == 8

    g: mhg.MHGraph = mhg.mhgraph([[1, 2, 3]]*8)
    assert len(list(generate_hyperbolic_cnfs(g))) == 1

    g: mhg.MHGraph = mhg.mhgraph([[1, 2], [2, 3]])
    assert len(list(generate_hyperbolic_cnfs(g))) == 8

    g: mhg.MHGraph = mhg.mhgraph([[1, 2], [2, 3], [1, 3]])
    assert len(list(generate_hyperbolic_cnfs(g))) == 8

    k4: mhg.MHGraph = mhg.mhgraph([[1, 2], [1, 3], [1, 4], [2, 3], [2, 4], [3, 4]])
    vertices: dict[graph.Vertex, int] = {1, 2, 3, 4}
    assert len(list(generate_hyperbolic_cnfs(k4))) == 2**4 * 3**4

    # This checks that every unsatisfiable Cnf on K4 is hyperbolic.
    for x in sat.cnfs_from_mhgraph(k4):
        if not sat.cnf_pysat_satcheck(x):
            assert hyperbolic_filter(vertices, x)

#! /usr/bin/env python3

import pytest
from ..unsat import *


def test_grid():
    graph_from_multiplicity_tuple = lambda graph_, mtup: \
        graph.graph(counter(dict(zip(sorted(graph_.keys()), mtup))))

    assert set(grid(graph.graph('x|y,y|z'))) \
        == {graph_from_multiplicity_tuple(graph.graph('x|y,y|z'), mtup)
            for mtup in [        (0, 1), (0, 2), (0, 3), (0, 4),
                         (1, 0), (1, 1), (1, 2), (1, 3), (1, 4),
                         (2, 0), (2, 1), (2, 2), (2, 3), (2, 4),
                         (3, 0), (3, 1), (3, 2), (3, 3), (3, 4),
                         (4, 0), (4, 1), (4, 2), (4, 3), (4, 4)]}

    assert set(grid(graph.graph('x|y,x|y'))) \
        == {graph_from_multiplicity_tuple(graph.graph('x|y,x|y'), mtup)
            for mtup in [(1, ), (2, ), (3, ), (4, )]}

    assert set(grid(graph.graph('x|y,x|y|z'))) \
        == {graph_from_multiplicity_tuple(graph.graph('x|y,x|y|z'), mtup)
            for mtup in [        (0, 1), (0, 2), (0, 3), (0, 4), (0, 5), (0, 6), (0, 7), (0, 8),
                         (1, 0), (1, 1), (1, 2), (1, 3), (1, 4), (1, 5), (1, 6), (1, 7), (1, 8),
                         (2, 0), (2, 1), (2, 2), (2, 3), (2, 4), (2, 5), (2, 6), (2, 7), (2, 8),
                         (3, 0), (3, 1), (3, 2), (3, 3), (3, 4), (3, 5), (3, 6), (3, 7), (3, 8),
                         (4, 0), (4, 1), (4, 2), (4, 3), (4, 4), (4, 5), (4, 6), (4, 7), (4, 8)]}


def test_knowledge():
    assert False, 'need to add tests'


def test_upper_cone():
    assert set(upper_cone(graph.graph(counter({'x|y': 1, 'x|y|z': 6})),
                          grid(graph.graph('x|y,x|y|z')))) \
        == {graph_from_multiplicity_tuple(graph_instance=graph.graph('x|y,x|y|z'),
                                          multiplicity_tuple=mtup)
            for mtup in [(1, 6), (1, 7), (1, 8),
                         (2, 6), (2, 7), (2, 8),
                         (3, 6), (3, 7), (3, 8),
                         (4, 6), (4, 7), (4, 8)]}

    assert set(upper_cone(graph.graph(counter({'x|y': 4, 'x|y|z': 8})),
                          grid(graph.graph('x|y,x|y|z')))) \
        == {graph_from_multiplicity_tuple(graph_instance=graph.graph('x|y,x|y|z'),
                                          multiplicity_tuple=(4,8))}


def test_lower_cone():
    assert set(lower_cone(graph.graph(counter({'x|y': 3, 'x|y|z': 5})),
                          grid(graph.graph('x|y,x|y|z')))) \
        == {graph_from_multiplicity_tuple(graph_instance=graph.graph('x|y,x|y|z'),
                                          multiplicity_tuple=mtup)
            for mtup in [(1, 1), (1, 2), (1, 3), (1, 4), (1, 5),
                         (2, 1), (2, 2), (2, 3), (2, 4), (2, 5),
                         (3, 1), (3, 2), (3, 3), (3, 4), (3, 5)]}

    assert set(lower_cone(graph.graph(counter({'x|y': 1, 'x|y|z': 1})),
                          grid(graph.graph('x|y,x|y|z')))) \
        == {graph_from_multiplicity_tuple(graph_instance=graph.graph('x|y,x|y|z'),
                                          multiplicity_tuple=(1,1))}


def test_grid_traversal():
    raise NotImplementedError("Missing tests")


def test_minimality_condition():
    raise NotImplementedError("Missing tests")


def test_minimal_unsat_graph():
    raise NotImplementedError("Missing tests")


def test_maximality_condition():
    raise NotImplementedError("Missing tests")


def test_maximal_sat_graphs():
    raise NotImplementedError("Missing tests")


def test_wisdom():
    raise NotImplementedError("Missing tests")


def test_add_wisdom_to_db():
    raise NotImplementedError("Missing tests")

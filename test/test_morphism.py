#! /usr/bin/env python3

import pytest
from ..morphism import *


def test_vertexmap():
    assert vertexmap({1: 11, 2: 12}, mhgraph.mhgraph([[1, 2]]), mhgraph.mhgraph([[11, 12, 13], [3, 2]]))
    assert vertexmap({1: 11, 2: 12}, mhgraph.mhgraph([[1, 2], [1, 2]]), mhgraph.mhgraph([[11, 12], [4, 2]]))
    assert vertexmap({1: 2, 2: 1}, mhgraph.mhgraph([[1, 2]]))
    assert vertexmap({1: 2}, mhgraph.mhgraph([[1]]), mhgraph.mhgraph([[2]]))
    with pytest.raises(ValueError):
        vertexmap({1: 2, 2: 1}, mhgraph.mhgraph([[1, 2, 3]]))
    with pytest.raises(ValueError):
        vertexmap({1: 11, 2: 12}, mhgraph.mhgraph([[1, 2]]))
    with pytest.raises(ValueError):
        vertexmap({}, mhgraph.mhgraph([[1, 2], [3, 4]]))


def test_injective_vertexmap():
    assert injective_vertexmap(vertexmap({1: 11, 2: 12},
                                         mhgraph.mhgraph([[1, 2], [1, 2]]),
                                         mhgraph.mhgraph([[11, 12], [3, 2]])))
    assert injective_vertexmap(vertexmap({1: 2, 2: 1},
                                         mhgraph.mhgraph([[1, 2]])))
    assert injective_vertexmap(vertexmap({1: 1}, mhgraph.mhgraph([[1]])))
    with pytest.raises(ValueError):
        injective_vertexmap(vertexmap({1: 3, 2: 3}, mhgraph.mhgraph([[1, 2]])))
    with pytest.raises(ValueError):
        injective_vertexmap(vertexmap({}, mhgraph.mhgraph([[1]])))


def test_graph_image():
    ivmap = lambda vm, g1, g2: injective_vertexmap(vertexmap(vm, g1, g2))
    assert graph_image(ivmap({11: 1, 12: 2}, mhgraph.mhgraph([[11], [11, 12]]), mhgraph.mhgraph([[1, 2]])),
                       mhgraph.mhgraph([[11], [11, 12]])) == mhgraph.mhgraph([[1], [1, 2]])

    assert graph_image(ivmap({11: 1, 12: 2, 13: 3},
                             mhgraph.mhgraph([[13, 11, 12], [11, 13], [12]]),
                             mhgraph.mhgraph([[1, 2, 3]])),
                       mhgraph.mhgraph([[13, 11, 12], [11, 13], [12]])) \
        == mhgraph.mhgraph([[2], [1, 3], [1, 2, 3]])

    assert graph_image(ivmap({11: 1, 12: 2},
                             mhgraph.mhgraph([[11, 12], [11, 12]]),
                             mhgraph.mhgraph([[1, 2]])), mhgraph.mhgraph([[11, 12], [11, 12]])) \
        == mhgraph.mhgraph([[1, 2], [1, 2]])


def test_morphism():
    morph = lambda vm, g1, g2: morphism(injective_vertexmap(vertexmap(vm, g1, g2)))
    mm = mhgraph.mhgraph
    assert morph({11: 1, 12: 2}, mm([[11, 12]]), mm([[1, 2]]))
    assert morph({11: 1, 12: 2}, mm([[11, 12], [11, 12]]), mm([[1, 2]]))
    assert morph({11: 1, 12: 2, 13: 3}, mm([[11, 12], [12, 13]]), mm([[1, 2], [2, 3]]))
    with pytest.raises(ValueError):
        morph({11: 1, 12: 3, 13: 2}, mm([[11, 12], [12, 13]]), mm([[1, 2], [2, 3]]))
    with pytest.raises(ValueError):
        morph({11: 1, 12: 3}, mm([[11, 12], [12, 13]]), mm([[1, 2], [2, 3]]))
    with pytest.raises(ValueError):
        morph({}, mm([[11]]), mm([[11]]))


def test_generate_vertexmaps():
    mh = mhgraph.hgraph
    inj = lambda vm, g1, g2: injective_vertexmap(vertexmap(vm, g1, g2))

    assert inj({1: 11, 2: 12}, mh([[1, 2], [1, 2]]), mh([[11, 12], [11, 12]])) \
        in generate_vertexmaps(mh([[1, 2], [1, 2]]), mh([[11, 12], [11, 12]]), True)
    assert inj({1: 12, 2: 11}, mh([[1, 2], [1, 2]]), mh([[11, 12], [11, 12]])) \
        in generate_vertexmaps(mh([[1, 2], [1, 2]]), mh([[11, 12], [11, 12]]), True)
    assert vertexmap({1: 11, 2: 11}, mh([[1, 2], [1, 2]]), mh([[11, 12], [11, 12]])) \
        not in generate_vertexmaps(mh([[1, 2], [1, 2]]), mh([[11, 12], [11, 12]]), True)
    assert vertexmap({1: 11, 2: 11}, mh([[1, 2], [1, 2]]), mh([[11, 12], [11, 12]])) \
        in generate_vertexmaps(mh([[1, 2], [1, 2]]), mh([[11, 12], [11, 12]]), False)


def test_subgraph_search():
    mm = mhgraph.mhgraph
    assert subgraph_search(mm([[1]]), mm([[11]])).translation == {1: 11}
    assert subgraph_search(mm([[1]]), mm([[11], [12]])).translation in [{1: 11}, {1: 12}]
    assert subgraph_search(mm([[1, 2]]), mm([[11, 12]])).translation \
        in [{1: 11, 2: 12}, {1: 12, 2: 11}]
    assert subgraph_search(mm([[1, 2]]), mm([[11, 12], [11]])).translation \
        in [{1: 11, 2: 12}, {1: 12, 2: 11}]
    assert subgraph_search(mm([[1, 2]]), mm([[11, 12], [11, 12]])).translation \
        in [{1: 11, 2: 12}, {1: 12, 2: 11}]
    assert subgraph_search(mm([[1, 2], [1, 2]]), mm([[11, 12], [11, 12]])).translation \
        in [{1: 11, 2: 12}, {1: 12, 2: 11}]
    assert subgraph_search(mm([[1, 2]]), mm([[11, 12], [13, 14]])).translation \
        in [{1: 11, 2: 12}, {1: 12, 2: 11}, {1: 13, 2: 14}, {1: 14, 2: 13}]
    assert subgraph_search(mm([[1]]), mm([[11, 12]])) is False
    assert subgraph_search(mm([[1, 2]]), mm([[1, 2, 3]])) is False


def test_isomorphism():
    mm = mhgraph.mhgraph
    assert isomorphism_search(mm([[1]]), mm([[11]])).translation == {1: 11}
    assert isomorphism_search(mm([[1], [2]]), mm([[11], [12]])).translation \
        in [{1: 11, 2: 12}, {1: 12, 2: 11}]
    assert isomorphism_search(mm([[1, 2]]), mm([[11, 12]])).translation \
        in [{1: 11, 2: 12}, {1: 12, 2: 11}]
    assert isomorphism_search(mm([[1, 2], [1]]), mm([[11], [11, 12]])).translation \
        == {1: 11, 2: 12}
    assert isomorphism_search(mm([[1, 2], [1, 2]]), mm([[11, 12], [11, 12]])).translation \
        in [{1: 11, 2: 12}, {1: 12, 2: 11}]
    assert isomorphism_search(mm([[1, 2]]), mm([[11, 12], [13, 14]])) is False
    assert isomorphism_search(mm([[1, 2]]), mm([[11, 12], [11, 12]])) is False
    assert isomorphism_search(mm([[1, 2]]), mm([[11, 12, 13]])) is False

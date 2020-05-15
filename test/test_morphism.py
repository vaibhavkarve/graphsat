#! /usr/bin/env python3

import pytest
import morphism
import graph
vm = morphism.vertexmap
mhg = morphism.mhgraph
ivm = morphism.injective_vertexmap
gvm = morphism.generate_vertexmaps
gi = morphism.graph_image
mm = morphism.morphism
hg = morphism.hgraph
ss = morphism.subgraph_search
iss = morphism.isomorphism_search


def test_graph_from_mhgraph():
    edges = [[1, 2], [2, 3], [1]]
    assert morphism.graph_from_mhgraph(mhg(edges)) == graph.graph(edges)
    with pytest.raises(ValueError):
        edges = [[1, 2], [1, 2]]
        morphism.graph_from_mhgraph(mhg(edges))
    with pytest.raises(ValueError):
        edges = [[1, 2, 3]]
        morphism.graph_from_mhgraph(mhg(edges))

def test_mhgraph_from_graph():
    edges = [[1, 2], [2, 3], [1]]
    assert morphism.mhgraph_from_graph(graph.graph(edges)) == mhg(edges)

def test_vertexmap():
    assert vm({1: 11, 2: 12}, mhg([[1, 2]]), mhg([[11, 12, 13], [3, 2]]))
    assert vm({1: 11, 2: 12}, mhg([[1, 2], [1, 2]]), mhg([[11, 12], [4, 2]]))
    assert vm({1: 2, 2: 1}, mhg([[1, 2]]))
    assert vm({1: 2}, mhg([[1]]), mhg([[2]]))
    assert vm({1: 2, 2: 1}, mhg([[1, 2, 3]])) is None
    assert vm({1: 11, 2: 12}, mhg([[1, 2]])) is None
    assert vm({}, mhg([[1, 2], [3, 4]])) is None


def test_injective_vertexmap():
    assert ivm(vm({1: 11, 2: 12}, mhg([[1, 2], [1, 2]]), mhg([[11, 12], [3, 2]])))
    assert ivm(vm({1: 2, 2: 1}, mhg([[1, 2]])))
    assert ivm(vm({1: 1}, mhg([[1]])))
    assert ivm(vm({1: 1, 2: 1}, mhg([[1, 2]]))) is None


def test_graph_image():
    ivmap = lambda vmap, g1, g2: ivm(vm(vmap, g1, g2))
    assert gi(ivmap({11: 1, 12: 2}, mhg([[11], [11, 12]]), mhg([[1, 2]])),
              mhg([[11], [11, 12]])) == mhg([[1], [1, 2]])

    assert gi(ivmap({11: 1, 12: 2, 13: 3},
                    mhg([[13, 11, 12], [11, 13], [12]]),
                    mhg([[1, 2, 3]])),
              mhg([[13, 11, 12], [11, 13], [12]])) == mhg([[2], [1, 3], [1, 2, 3]])

    assert gi(ivmap({11: 1, 12: 2}, mhg([[11, 12], [11, 12]]),
                    mhg([[1, 2]])), mhg([[11, 12], [11, 12]])) == mhg([[1, 2], [1, 2]])


def test_morphism():
    morph = lambda vmap, g1, g2: mm(ivm(vm(vmap, g1, g2))) # noqa
    assert morph({11: 1, 12: 2}, mhg([[11, 12]]), mhg([[1, 2]]))
    assert morph({11: 1, 12: 2}, mhg([[11, 12], [11, 12]]), mhg([[1, 2]]))
    assert morph({11: 1, 12: 2, 13: 3}, mhg([[11, 12], [12, 13]]), mhg([[1, 2], [2, 3]]))
    assert not morph({11: 1, 12: 3, 13: 2}, mhg([[11, 12], [12, 13]]),
                     mhg([[1, 2], [2, 3]]))


def test_generate_vertexmaps():
    inj = lambda vmap, g1, g2: ivm(vm(vmap, g1, g2))
    hg1, hg2 = hg([[1, 2], [1, 2]]), hg([[11, 12], [11, 12]])
    assert inj({1: 11, 2: 12}, hg1, hg2) in gvm(hg1, hg2)
    assert inj({1: 12, 2: 11}, hg1, hg2) in gvm(hg1, hg2)
    assert vm({1: 11, 2: 11}, hg1, hg2) not in gvm(hg1, hg2)
    assert vm({1: 11, 2: 11}, hg1, hg2) not in gvm(hg1, hg2)

    assert inj({1: 1, 2: 2}, hg1, None) in gvm(hg1)
    assert inj({1: 2, 2: 1}, hg1, None) in gvm(hg1)
    assert vm({1: 1, 2: 1}, hg1) not in gvm(hg1)
    assert vm({1: 1, 2: 1}, hg1) not in gvm(hg1)

    assert vm({1: 1, 2: 1}, hg1, None) in gvm(hg1, None, False)
    assert vm({1: 1, 2: 1}, hg1, None) in gvm(hg1, None, False)


def test_subgraph_search():
    assert ss(mhg([[1]]), mhg([[11]]))[1].translation == {1: 11}
    assert ss(mhg([[1]]), mhg([[11], [12]]))[1].translation in [{1: 11}, {1: 12}]
    assert ss(mhg([[1, 2]]), mhg([[11, 12]]))[1].translation \
        in [{1: 11, 2: 12}, {1: 12, 2: 11}]
    assert ss(mhg([[1, 2]]), mhg([[11, 12], [11]]))[1].translation \
        in [{1: 11, 2: 12}, {1: 12, 2: 11}]
    assert ss(mhg([[1, 2]]), mhg([[11, 12], [11, 12]]))[1].translation \
        in [{1: 11, 2: 12}, {1: 12, 2: 11}]
    assert ss(mhg([[1, 2], [1, 2]]), mhg([[11, 12], [11, 12]]))[1].translation \
        in [{1: 11, 2: 12}, {1: 12, 2: 11}]
    assert ss(mhg([[1, 2]]), mhg([[11, 12], [13, 14]]))[1].translation \
        in [{1: 11, 2: 12}, {1: 12, 2: 11}, {1: 13, 2: 14}, {1: 14, 2: 13}]
    assert ss(mhg([[1, 2], [2, 3]]), mhg([[1, 2], [1, 2]])) == (False, None)
    assert ss(mhg([[1]]), mhg([[11, 12]])) == (False, None)
    assert ss(mhg([[1, 2]]), mhg([[1, 2, 3]])) == (False, None)
    assert len(list(ss(mhg([[1, 2]]), mhg([[11, 12], [13, 14]]), True)[1])) == 4
    


def test_isomorphism_search():
    assert iss(mhg([[1]]), mhg([[11]]))[1].translation == {1: 11}
    assert iss(mhg([[1], [2]]), mhg([[11], [12]]))[1].translation \
        in [{1: 11, 2: 12}, {1: 12, 2: 11}]
    assert iss(mhg([[1, 2]]), mhg([[11, 12]]))[1].translation \
        in [{1: 11, 2: 12}, {1: 12, 2: 11}]
    assert iss(mhg([[1, 2], [1]]), mhg([[11], [11, 12]]))[1].translation \
        == {1: 11, 2: 12}
    assert iss(mhg([[1, 2], [1, 2]]), mhg([[11, 12], [11, 12]]))[1].translation \
        in [{1: 11, 2: 12}, {1: 12, 2: 11}]
    assert iss(mhg([[1, 2]]), mhg([[11, 12], [13, 14]])) == (False, None)
    assert iss(mhg([[1, 2]]), mhg([[11, 12], [11, 12]])) == (False, None)
    assert iss(mhg([[1, 2]]), mhg([[11, 12, 13]])) == (False, None)

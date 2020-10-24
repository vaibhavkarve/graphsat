#! /usr/bin/env python3

import pytest
import graphsat.morphism as morphism
from graphsat.mhgraph import mhgraph, hgraph
vm = morphism.vertexmap
mhg = mhgraph
ivm = morphism.injective_vertexmap
gvm = morphism.generate_vertexmaps
gi = morphism.graph_image
mm = morphism.morphism
hg = hgraph
ss = morphism.subgraph_search
iss = morphism.isomorphism_search

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


def test_graph_image():
    ivmap = lambda vmap, g1, g2: ivm(vm(vmap, g1, g2))  # noqa
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
    inj = lambda vmap, g1, g2: ivm(vm(vmap, g1, g2))  # noqa
    assert inj({1: 11, 2: 12}, hg([[1, 2], [1, 2]]), hg([[11, 12], [11, 12]])) \
        in gvm(hg([[1, 2], [1, 2]]), hg([[11, 12], [11, 12]]), True)
    assert inj({1: 12, 2: 11}, hg([[1, 2], [1, 2]]), hg([[11, 12], [11, 12]])) \
        in gvm(hg([[1, 2], [1, 2]]), hg([[11, 12], [11, 12]]), True)
    assert vm({1: 11, 2: 11}, hg([[1, 2], [1, 2]]), hg([[11, 12], [11, 12]])) \
        not in gvm(hg([[1, 2], [1, 2]]), hg([[11, 12], [11, 12]]), True)
    assert vm({1: 11, 2: 11}, hg([[1, 2], [1, 2]]), hg([[11, 12], [11, 12]])) \
        in gvm(hg([[1, 2], [1, 2]]), hg([[11, 12], [11, 12]]), False)


@pytest.mark.parametrize(
    'mhg1,mhg2,translation',
    [([[1]], [[11]], [{1: 11}]),
     ([[1]], [[11], [12]], [{1: 11}, {1: 12}]),
     ([[1, 2]], [[11, 12]], [{1: 11, 2: 12}, {1 : 12, 2: 11}]),
     ([[1, 2]], [[11, 12], [11]], [{1: 11, 2: 12}, {1: 12, 2: 11}]),
     ([[1, 2]], [[11, 12], [11, 12]], [{1: 11, 2: 12}, {1: 12, 2: 11}]),
     ([[1, 2], [1, 2]], [[11, 12], [11, 12]], [{1: 11, 2: 12}, {1: 12, 2: 11}]),
     ([[1, 2]], [[11, 12], [13, 14]],
      [{1: 11, 2: 12}, {1: 12, 2: 11}, {1: 13, 2:14}, {1: 14, 2: 13}])])
def test_subgraph_search(mhg1, mhg2, translation):
    assert ss(mhg(mhg1), mhg(mhg2), return_all=False)[1].translation in translation

@pytest.mark.parametrize('return_all', [(True,), (False,)])
def test_subgraph_search2(return_all):
    assert ss(mhg([[1]]), mhg([[11, 12]]), return_all) == (False, None)
    assert ss(mhg([[1, 2]]), mhg([[1, 2, 3]]), return_all) == (False, None)


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

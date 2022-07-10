#! /usr/bin/env python3.8

from typing import Callable, Mapping, cast, Iterator

import pytest

import graphsat.morphism as morphism
from graphsat.graph import Vertex, vertex
from graphsat.mhgraph import HGraph, MHGraph, hgraph, mhgraph

vm = morphism.vertexmap
mhg = mhgraph
ivm = morphism.injective_vertexmap
gvm = morphism.generate_vertexmaps
gi = morphism.graph_image
mm = morphism.morphism
hg = hgraph
ss = morphism.subgraph_search
iss = morphism.isomorphism_search
vv = vertex

def test_vertexmap() -> None:
    assert vm({vv(1): vv(11), vv(2): vv(12)}, hg([[1, 2]]), hg([[11, 12, 13], [3, 2]]))
    assert vm({vv(1): vv(11), vv(2): vv(12)}, hg([[1, 2], [1, 2]]), hg([[11, 12], [4, 2]]))
    assert vm({vv(1): vv(2), vv(2): vv(1)}, hg([[1, 2]]))
    assert vm({vv(1): vv(2)}, hg([[1]]), hg([[2]]))
    assert vm({vv(1): vv(2), vv(2): vv(1)}, hg([[1, 2, 3]])) is None
    assert vm({vv(1): vv(11), vv(2): vv(12)}, hg([[1, 2]])) is None
    assert vm({}, hg([[1, 2], [3, 4]])) is None


def test_injective_vertexmap() -> None:
    assert ivm(cast(morphism.VertexMap,
                    vm({vv(1): vv(11), vv(2): vv(12)}, hg([[1, 2], [1, 2]]), hg([[11, 12], [3, 2]]))))
    assert ivm(cast(morphism.VertexMap,
                    vm({vv(1): vv(2), vv(2): vv(1)}, hg([[1, 2]]))))
    assert ivm(cast(morphism.VertexMap,
                    vm({vv(1): vv(1)}, hg([[1]]))))


def test_graph_image() -> None:
    ivmap: Callable[[Mapping[Vertex, Vertex], HGraph, HGraph], morphism.InjectiveVertexMap | None]
    ivmap = lambda vmap, g1, g2: ivm(cast(morphism.VertexMap,
                                          vm(vmap, g1, g2)))
    assert gi(cast(morphism.InjectiveVertexMap,
                   ivmap({vv(11): vv(1), vv(12): vv(2)},
                         hg([[11], [11, 12]]), hg([[1, 2]]))),
              mhg([[11], [11, 12]])) == mhg([[1], [1, 2]])

    assert gi(cast(morphism.InjectiveVertexMap,
                   ivmap({vv(11): vv(1), vv(12): vv(2), vv(13): vv(3)},
                         hg([[13, 11, 12], [11, 13], [12]]),
                         hg([[1, 2, 3]]))),
              mhg([[13, 11, 12], [11, 13], [12]])) == mhg([[2], [1, 3], [1, 2, 3]])

    assert gi(cast(morphism.InjectiveVertexMap,
                   ivmap({vv(11): vv(1), vv(12): vv(2)}, hg([[11, 12], [11, 12]]),
                         hg([[1, 2]]))),
              mhg([[11, 12], [11, 12]])) == mhg([[1, 2], [1, 2]])


def test_morphism() -> None:
    morph: Callable[[Mapping[Vertex, Vertex], HGraph, HGraph], morphism.Morphism | None]
    morph = lambda vmap, g1, g2: mm(cast(morphism.InjectiveVertexMap,
                                         ivm(cast(morphism.VertexMap,
                                                  vm(vmap, g1, g2)))))
    assert morph({vv(11): vv(1), vv(12): vv(2)}, hg([[11, 12]]), hg([[1, 2]]))
    assert morph({vv(11): vv(1), vv(12): vv(2)}, hg([[11, 12], [11, 12]]), hg([[1, 2]]))
    assert morph({vv(11): vv(1), vv(12): vv(2), vv(13): vv(3)}, hg([[11, 12], [12, 13]]), hg([[1, 2], [2, 3]]))
    assert not morph({vv(11): vv(1), vv(12): vv(3), vv(13): vv(2)}, hg([[11, 12], [12, 13]]),
                     hg([[1, 2], [2, 3]]))


def test_generate_vertexmaps() -> None:
    inj: Callable[[Mapping[Vertex, Vertex], HGraph, HGraph], None | morphism.InjectiveVertexMap]
    inj = lambda vmap, g1, g2: ivm(cast(morphism.VertexMap,
                                        vm(vmap, g1, g2)))
    assert inj({vv(1): vv(11), vv(2): vv(12)}, hg([[1, 2], [1, 2]]), hg([[11, 12], [11, 12]])) \
        in list(gvm(hg([[1, 2], [1, 2]]), hg([[11, 12], [11, 12]]), True))
    assert inj({vv(1): vv(12), vv(2): vv(11)}, hg([[1, 2], [1, 2]]), hg([[11, 12], [11, 12]])) \
        in list(gvm(hg([[1, 2], [1, 2]]), hg([[11, 12], [11, 12]]), True))
    assert vm({vv(1): vv(11), vv(2): vv(11)}, hg([[1, 2], [1, 2]]), hg([[11, 12], [11, 12]])) \
        not in list(gvm(hg([[1, 2], [1, 2]]), hg([[11, 12], [11, 12]]), True))
    assert vm({vv(1): vv(11), vv(2): vv(11)}, hg([[1, 2], [1, 2]]), hg([[11, 12], [11, 12]])) \
        in list(gvm(hg([[1, 2], [1, 2]]), hg([[11, 12], [11, 12]]), False))


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
def test_subgraph_search(mhg1: MHGraph, mhg2: MHGraph, translation: Mapping[Vertex, Vertex]) -> None:
    assert cast(morphism.Morphism,
                     ss(mhg(mhg1), mhg(mhg2), return_all=False)[1]).translation in translation

@pytest.mark.parametrize('return_all', [(True,), (False,)])
def test_subgraph_search2(return_all: bool) -> None:
    assert ss(mhg([[1]]), mhg([[11, 12]]), return_all) == (False, None)
    assert ss(mhg([[1, 2]]), mhg([[1, 2, 3]]), return_all) == (False, None)


def test_isomorphism_search() -> None:
    assert cast(morphism.Morphism, iss(mhg([[1]]), mhg([[11]]))[1]).translation == {1: 11}
    assert cast(morphism.Morphism, iss(mhg([[1], [2]]), mhg([[11], [12]]))[1]).translation \
        in [{1: 11, 2: 12}, {1: 12, 2: 11}]
    assert cast(morphism.Morphism, iss(mhg([[1, 2]]), mhg([[11, 12]]))[1]).translation \
        in [{1: 11, 2: 12}, {1: 12, 2: 11}]
    assert cast(morphism.Morphism, iss(mhg([[1, 2], [1]]), mhg([[11], [11, 12]]))[1]).translation \
        == {1: 11, 2: 12}
    assert cast(morphism.Morphism, iss(mhg([[1, 2], [1, 2]]), mhg([[11, 12], [11, 12]]))[1]).translation \
        in [{1: 11, 2: 12}, {1: 12, 2: 11}]
    assert iss(mhg([[1, 2]]), mhg([[11, 12], [13, 14]])) == (False, None)
    assert iss(mhg([[1, 2]]), mhg([[11, 12], [11, 12]])) == (False, None)
    assert iss(mhg([[1, 2]]), mhg([[11, 12, 13]])) == (False, None)

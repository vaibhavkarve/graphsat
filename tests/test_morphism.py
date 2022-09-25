#! /usr/bin/env python3.10

from typing import Callable, Mapping, cast

import pytest

from graphsat.graph import Vertex, vertex
from graphsat.mhgraph import HGraph, MHGraph, hgraph, mhgraph
from graphsat.morphism import (InjectiveVertexMap, Morphism, VertexMap,
                               generate_vertexmaps, graph_image,
                               injective_vertexmap, isomorphism_search,
                               morphism, subgraph_search, vertexmap)


def test_vertexmap() -> None:
    assert vertexmap({vertex(1): vertex(11), vertex(2): vertex(12)},
                     hgraph([[1, 2]]), hgraph([[11, 12, 13], [3, 2]]))
    assert vertexmap({vertex(1): vertex(11), vertex(2): vertex(12)},
                     hgraph([[1, 2], [1, 2]]), hgraph([[11, 12], [4, 2]]))
    assert vertexmap({vertex(1): vertex(2), vertex(2): vertex(1)}, hgraph([[1, 2]]))
    assert vertexmap({vertex(1): vertex(2)}, hgraph([[1]]), hgraph([[2]]))
    assert vertexmap({vertex(1): vertex(2), vertex(2): vertex(1)}, hgraph([[1, 2, 3]])) is None
    assert vertexmap({vertex(1): vertex(11), vertex(2): vertex(12)}, hgraph([[1, 2]])) is None
    assert vertexmap({}, hgraph([[1, 2], [3, 4]])) is None


def test_injective_vertexmap() -> None:
    assert injective_vertexmap(
        cast(VertexMap,
             vertexmap({vertex(1): vertex(11), vertex(2): vertex(12)},
                       hgraph([[1, 2], [1, 2]]), hgraph([[11, 12], [3, 2]]))))
    assert injective_vertexmap(cast(VertexMap,
                    vertexmap({vertex(1): vertex(2), vertex(2): vertex(1)}, hgraph([[1, 2]]))))
    assert injective_vertexmap(cast(VertexMap,
                    vertexmap({vertex(1): vertex(1)}, hgraph([[1]]))))


def test_graph_image() -> None:
    ivmap: Callable[[Mapping[Vertex, Vertex], HGraph, HGraph], InjectiveVertexMap | None]
    ivmap = lambda vmap, g1, g2: injective_vertexmap(cast(VertexMap,
                                          vertexmap(vmap, g1, g2)))
    assert graph_image(cast(InjectiveVertexMap,
                   ivmap({vertex(11): vertex(1), vertex(12): vertex(2)},
                         hgraph([[11], [11, 12]]), hgraph([[1, 2]]))),
              mhgraph([[11], [11, 12]])) == mhgraph([[1], [1, 2]])

    assert graph_image(cast(InjectiveVertexMap,
                   ivmap({vertex(11): vertex(1), vertex(12): vertex(2), vertex(13): vertex(3)},
                         hgraph([[13, 11, 12], [11, 13], [12]]),
                         hgraph([[1, 2, 3]]))),
              mhgraph([[13, 11, 12], [11, 13], [12]])) == mhgraph([[2], [1, 3], [1, 2, 3]])

    assert graph_image(cast(InjectiveVertexMap,
                   ivmap({vertex(11): vertex(1), vertex(12): vertex(2)}, hgraph([[11, 12], [11, 12]]),
                         hgraph([[1, 2]]))),
              mhgraph([[11, 12], [11, 12]])) == mhgraph([[1, 2], [1, 2]])


def test_morphism() -> None:
    morph: Callable[[Mapping[Vertex, Vertex], HGraph, HGraph], Morphism | None]
    morph = lambda vmap, g1, g2: morphism(cast(InjectiveVertexMap,
                                               injective_vertexmap(cast(VertexMap,
                                                  vertexmap(vmap, g1, g2)))))
    assert morph({vertex(11): vertex(1), vertex(12): vertex(2)},
                 hgraph([[11, 12]]), hgraph([[1, 2]]))
    assert morph({vertex(11): vertex(1), vertex(12): vertex(2)},
                 hgraph([[11, 12], [11, 12]]), hgraph([[1, 2]]))
    assert morph({vertex(11): vertex(1), vertex(12): vertex(2), vertex(13): vertex(3)},
                 hgraph([[11, 12], [12, 13]]), hgraph([[1, 2], [2, 3]]))
    assert not morph({vertex(11): vertex(1), vertex(12): vertex(3), vertex(13): vertex(2)},
                     hgraph([[11, 12], [12, 13]]), hgraph([[1, 2], [2, 3]]))


def test_generate_vertexmaps() -> None:
    inj: Callable[[Mapping[Vertex, Vertex], HGraph, HGraph], None | InjectiveVertexMap]
    inj = lambda vmap, g1, g2: injective_vertexmap(cast(VertexMap,
                                        vertexmap(vmap, g1, g2)))
    assert inj({vertex(1): vertex(11), vertex(2): vertex(12)},
               hgraph([[1, 2], [1, 2]]), hgraph([[11, 12], [11, 12]])) \
        in list(generate_vertexmaps(hgraph([[1, 2], [1, 2]]), hgraph([[11, 12], [11, 12]]), True))
    assert inj({vertex(1): vertex(12), vertex(2): vertex(11)},
               hgraph([[1, 2], [1, 2]]), hgraph([[11, 12], [11, 12]])) \
        in list(generate_vertexmaps(hgraph([[1, 2], [1, 2]]), hgraph([[11, 12], [11, 12]]), True))
    assert vertexmap({vertex(1): vertex(11), vertex(2): vertex(11)},
                     hgraph([[1, 2], [1, 2]]), hgraph([[11, 12], [11, 12]])) \
        not in list(generate_vertexmaps(hgraph([[1, 2], [1, 2]]), hgraph([[11, 12], [11, 12]]), True))
    assert vertexmap({vertex(1): vertex(11), vertex(2): vertex(11)},
                     hgraph([[1, 2], [1, 2]]), hgraph([[11, 12], [11, 12]])) \
        in list(generate_vertexmaps(hgraph([[1, 2], [1, 2]]), hgraph([[11, 12], [11, 12]]), False))


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
def test_subgraph_search(mhg1: MHGraph, mhg2: MHGraph,
                         translation: list[dict[Vertex, Vertex]]) -> None:
    assert cast(Morphism, subgraph_search(
        mhgraph(mhg1), mhgraph(mhg2), return_all=False)[1]).translation in translation

@pytest.mark.parametrize('return_all', [(True,), (False,)])
def test_subgraph_search2(return_all: bool) -> None:
    assert subgraph_search(mhgraph([[1]]), mhgraph([[11, 12]]), return_all) == (False, None)
    assert subgraph_search(mhgraph([[1, 2]]), mhgraph([[1, 2, 3]]), return_all) == (False, None)


def test_isomorphism_search() -> None:
    assert cast(Morphism, isomorphism_search(mhgraph([[1]]),
                                             mhgraph([[11]]))[1]).translation == {1: 11}
    assert cast(Morphism, isomorphism_search(mhgraph([[1], [2]]),
                                             mhgraph([[11], [12]]))[1]).translation \
        in [{1: 11, 2: 12}, {1: 12, 2: 11}]
    assert cast(Morphism, isomorphism_search(mhgraph([[1, 2]]),
                                             mhgraph([[11, 12]]))[1]).translation \
        in [{1: 11, 2: 12}, {1: 12, 2: 11}]
    assert cast(Morphism, isomorphism_search(mhgraph([[1, 2], [1]]),
                                             mhgraph([[11], [11, 12]]))[1]).translation \
        == {1: 11, 2: 12}
    assert cast(Morphism, isomorphism_search(mhgraph([[1, 2], [1, 2]]),
                                             mhgraph([[11, 12], [11, 12]]))[1]).translation \
        in [{1: 11, 2: 12}, {1: 12, 2: 11}]
    assert isomorphism_search(mhgraph([[1, 2]]),
                              mhgraph([[11, 12], [13, 14]])) == (False, None)
    assert isomorphism_search(mhgraph([[1, 2]]),
                              mhgraph([[11, 12], [11, 12]])) == (False, None)
    assert isomorphism_search(mhgraph([[1, 2]]),
                              mhgraph([[11, 12, 13]])) == (False, None)

#!/usr/bin/env python3
"""All functions that work on Graphs, HGraphs and MHGraphs live here.

This includes an implementation of the brute-force subgraph search algorithm and a
brute-force isomorphism search algorithm for MHGraphs.
"""

import itertools as it
from typing import (AbstractSet, cast, Dict, Iterator, KeysView, List, Mapping,
                    NamedTuple, NewType, Optional, Tuple, Union)

import more_itertools as mit  # type: ignore
from loguru import logger

from graphsat.graph import graph, Graph, Vertex
from graphsat.mhgraph import hgraph, HGraph, mhgraph, MHGraph, vertices

# Types
# =====

#: `Translation` is an alias for ``Dict[Vertex, Vertex]``.
Translation = Dict[Vertex, Vertex]

#: `VertexMap` is a `collections.NamedTuple` with three named entries --- a `domain`
#: HGraph  (called ``hgraph1``), a `codomain` HGraph (called ``hgraph2``), and a
#: Translation dictionary (called ``translation``) between the Vertices of the two
#: HGraphs.
VertexMap = NamedTuple('VertexMap',
                       [('hgraph1', HGraph),
                        ('hgraph2', HGraph),
                        ('translation', Translation)])

InjectiveVertexMap = NewType('InjectiveVertexMap', VertexMap)
InjectiveVertexMap.__doc__ = """`InjectiveVertexMap` is a subtype of `VertexMap`."""

Morphism = NewType('Morphism', InjectiveVertexMap)
Morphism.__doc__ = """`Morphism` is a subtype of `InjectiveVertexMap`."""


# Conversion Functions
# ====================


def graph_from_mhgraph(mhg: MHGraph) -> Graph:
    """Obtain a simple Graph from a MHGraph if possible. If not, raise a ValueError.

    A MHGraph can be converted to a simple Graph if:
    - it has no hyper-edges,
    - its edges have no multiplicities.

    Args:
       mhg (:obj:`MHGraph`): a MHGraph which can be coerced to a
          simple graph.

    Return:
       A simple Graph with the same Edges as ``mhg``, but with multiplicities
       removed.

    Raises:
       AssertionError: if ``mhg`` cannot be coerced to a simple graph.

    """
    assert all(multiplicity == 1 for multiplicity in mhg.values()),\
               'Multi-edges cannot be coerced to simple edges.'
    return graph(mhg.keys())


def hgraph_from_mhgraph(mhg: MHGraph) -> HGraph:
    """Obtain a HGraph by ignoring the HEdge-multiplicities of a hgraph.

    Args:
       mhg (:obj:`MHGraph`)

    Return:
       A HGraph with the same HEdges as ``mhg``, but with multiplicities
       removed.

    """
    return hgraph(mhg.keys())


def mhgraph_from_graph(graph_instance: Graph) -> MHGraph:
    """Obtain a MHGraph from a mhgraph.

    Every Graph is also a MHGraph (after some coercion).

    Args:
       graph_instance (:obj:`Graph`)

    Return:
       A MHGraph whose HEdges are the Edges of ``graph_instance`` with HEdge-multiplicity
       one.

    """
    return mhgraph(graph_instance)


# Constructor Functions
# =====================


def vertexmap(translation: Mapping[Vertex, Vertex],
              hgraph1: HGraph,
              hgraph2: Optional[HGraph] = None) -> Optional[VertexMap]:
    """Check if a Translation is a VertexMap from one HGraph to another.

    A Translation is a `VertexMap` if its keys are **all** the Vertices of the domain
    HGraph and its values are a subset of the Vertices of the codomain HGraph.

    .. note::

       * The empty translation is never a VertexMap because a HGraph is not allowed to be
         empty.

    Args:
       translation (:obj:`Translation`): a Translation dict from all Vertices of
          ``hgraph1`` to a subset of the Vertices of ``hgraph2``.
       graph1 (:obj:`HGraph`): the domain H
       graph2 (:obj:`HGraph`, optional): the codomain H If ``hgraph2`` is
          not provided, then check whether the given Translation is a VertexMap from
          ``hgraph1`` to itself.

    Return:
       * a VertexMap named-tuple.
       * return ``None`` if not every Vertex of ``hgraph1`` is a key of ``translation``.
       * return ``None`` if the values of ``translation`` are not a subset of the Vertices
         of ``hgraph2``.
    """
    if hgraph2 is None:
        hgraph2 = hgraph1

    keys_are_all_vertices: bool
    keys_are_all_vertices = translation.keys() == vertices(hgraph1)

    values_are_subset_of_vertices: bool
    values_are_subset_of_vertices = set(translation.values()) <= vertices(hgraph2)

    if not keys_are_all_vertices or not values_are_subset_of_vertices:
        return None
    return VertexMap(hgraph1, hgraph2, translation=dict(translation))


def injective_vertexmap(vmap: VertexMap) -> Optional[InjectiveVertexMap]:
    """Check if a VertexMap is injective.

    A VertexMap is `injective` if its Translation dictionary is, i.e. if its translation
    has the same number of keys and values.

    Args:
       vmap (:obj:`VertexMap`): a VertexMap named-tuple.

    Return:
       ``vmap`` after casting to an InjectiveVertexMap named-tuple. Return ``None`` if
          ``vmap`` is not injective.
    """
    if len(vmap.translation.keys()) != len(set(vmap.translation.values())):
        return None
    return InjectiveVertexMap(vmap)


def graph_image(ivmap: InjectiveVertexMap, mhg: MHGraph) -> MHGraph:
    """Return the image of a MHGraph under an InjectiveVertexMap.

    .. note::
       this function is guaranteed to always return a valid MHGraph because:

       1. the axioms of VertexMap ensure that all Vertices of the domain MHGraph are
          mapped.
       2. the axioms of InjectiveVertexMap prevent repetition of a Vertex in any single
          HEdge of the image, i.e. they prevent collapse of HEdges.
       3. the axioms of InjectiveVertexMap also imply that if the domain MHGraph has all
          HEdge-multiplicities equal to one, then so will the image mhgraph.

    Args:
        ivmap (:obj:`InjectiveVertexMap`): an InjectiveVertexMap named-tuple.
        mhg (:obj:`MHGraph`): the MHGraph to be translated/mapped.

    Return:
       A MHGraph formed by mapping the Vertices of ``mhg`` using
       ``ivmap.translation``, while keeping the adjacency of Vertices of
       ``mhg`` intact.

    """
    assert set(ivmap.translation.keys()) <= vertices(mhg), \
        f'InjectiveVertexMap keys should be vertices of {mhg = }'
    mapped_mhgraph: List[List[Vertex]]
    mapped_mhgraph = [[ivmap.translation[vertex] for vertex in hedge] for hedge in
                      mhg.elements()]
    return mhgraph(mapped_mhgraph)


def morphism(ivmap: InjectiveVertexMap) -> Optional[Morphism]:
    """Check if an InjectiveVertexMap is a Morphism.

    A `Morphism` (which is short for HGraph-homomophism) is an InjectiveVertexMap
    such that adjacent Vertices of the domain HGraph are mapped to adjacent vertices
    in the codomain HGraph.

    .. note::
       1. Injectivity ensures that HEdges do not get mapped to collapsed HEdges.
       2. Morphisms ignore HEdge-multiplicities.
       3. Not every InjectiveVertexMap is a Morphism.
       4. An empty dictionary is not a VertexMap translation and therefore not a Morphism
          translation.

    Args:
       ivmap (:obj:`InjectiveVertexMap`): an InjectiveVertexMap named-tuple.

    Return:
       ``ivmap`` cast as a Morphism named-tuple. Return ``None`` if a HEdge of
       ``ivmap.hgraph1`` gets mapped to a HEdge under ``ivmap.translation`` that is not an
       HEdge of ``ivmap.hgraph2``.
    """
    mapped_hedges: KeysView[AbstractSet[Vertex]]
    mapped_hedges = graph_image(ivmap, mhgraph(ivmap.hgraph1)).keys()

    if not all(hedge in ivmap.hgraph2 for hedge in mapped_hedges):
        return None
    return Morphism(ivmap)


# Higher (MH)Graph Operations
# ===========================


def generate_vertexmaps(hgraph1: HGraph,
                        hgraph2: Optional[HGraph] = None,
                        injective: bool = True) -> Iterator[Union[VertexMap, InjectiveVertexMap]]:
    """Generate all the (Injective)VertexMaps from domain HGraph to codomain HGraph.

    Args:
       hgraph1 (:obj:`HGraph`): the domain HGraph.
       hgraph2 (:obj:`HGraph`, optional): the codomain HGraph. If ``hgraph2`` is
          not provided (default), then generate all (Injective)VertexMaps from ``hgraph1`` to
          itself.
       injective (:obj:`bool`, optional): if set to ``True`` (default), then generate all
          the InjectiveVertexMaps from ``hgraph1`` to ``hgraph2``. If set to ``False``,
          then generate all the VertexMaps from ``hgraph1`` to ``hgraph2``.

    Algorithm:
       * Set of (Injective)VertexMap from ``hgraph1`` to ``hgraph2`` is formed by taking
         the Cartesian product of the `Domain` and `Codomain`.
       * Here, the `Domain` consists of all permutations of the Vertices of the domain
         HGraph (i.e. the order matters in the Domain).
       * The `Codomain` consists of all combinations (without or with replacement, if
         ``injective`` is ``True` or ``False`` respectively) of the Vertices of the
         codomain
         HGraph (i.e. the order does not matter in the Codomain).

    Return:
       An Iterator of (Injective)VertexMaps from ``hgraph1`` to ``hgraph2``.

    """
    if hgraph2 is None:
        hgraph2 = hgraph1

    domain: Iterator[Tuple[Vertex, ...]]
    domain = it.permutations(vertices(hgraph1))

    combinatorial_scheme = it.combinations if injective \
        else it.combinations_with_replacement

    codomain: Iterator[Tuple[Vertex, ...]]
    codomain = combinatorial_scheme(vertices(hgraph2), len(vertices(hgraph1)))

    mappings1: Iterator[Tuple[Tuple[Vertex, ...], Tuple[Vertex, ...]]]
    mappings1 = it.product(domain, codomain)

    mappings2: Iterator[Iterator[Tuple[Vertex, Vertex]]]
    mappings2 = (zip(*pair) for pair in mappings1)

    translations: Iterator[Translation]
    translations = map(dict, mappings2)

    vertexmaps_optional: Iterator[Optional[VertexMap]]
    vertexmaps_optional = map(lambda t: vertexmap(t, hgraph1, hgraph2), translations)

    vertexmaps: Iterator[VertexMap]
    vertexmaps = filter(None, vertexmaps_optional)

    if not injective:
        return vertexmaps

    injective_vertexmaps: Iterator[InjectiveVertexMap]
    injective_vertexmaps = filter(None, map(injective_vertexmap, vertexmaps))

    return injective_vertexmaps


def is_immediate_subgraph(mhgraph1: MHGraph, mhgraph2: MHGraph) -> bool:
    """Check if the domain MHGraph is an immediate-subgraph of the codomain.

    We say that the domain MHGraph is an `immediate subgraph` of the codomain MHGraph if
    every HEdge in the domain MHGraph (with multiplicity ``m``) is in the codomain MHGraph
    with multiplicity no less than ``m``.

    Args:
       mhgraph1 (:obj:`MHGraph`)
       mhgraph2 (:obj:`MHGraph`)

    Return:
       ``True`` if every HEdge of ``mhgraph1`` with multiplicity ``m`` is a HEdge of
       ``mhgraph2`` with multiplicity no less than ``m``, else return ``False``.

    """
    return all(hedge in mhgraph2 and mult <= mhgraph2[hedge]
               for hedge, mult in mhgraph1.items())


def subgraph_search(mhgraph1: MHGraph, mhgraph2: MHGraph, return_all: bool = False) \
        -> Tuple[bool, Union[None, Morphism, Iterator[Morphism]]]:
    """Brute-force subgraph search algorithm extended to MHGraphs.

    ``mhgraph1`` is a `subgraph` of ``mhgraph2`` if there is a Morphism with domain HGraph
    as ``hgraph_from_mhgraph(mhgraph1)`` and codomain HGraph as
    ``hgraph_from_mhgraph(mhgraph2)`` such that every HEdge of ``mhgraph1`` maps to a
    unique HEdge (also accounting for multiplicities) of ``mhgraph2`` under the
    Translation dictionary.

    Algorithm:
       * First perform some heuristic checks
       * If the two MHGraphs pass the heuristic checks, then generate all Morphisms from
         ``hgraph_from_mhgraph(mhgraph1)`` to ``hgraph_from_mhgraph(mhgraph2)``.
       * Find the image of ``hgraph_from_mhgraph(mhgraph1)`` under each Morphism.
       * Check that each HEdge of the image HGraph is present with higher multiplicity in
         the codomain.
          * If yes, and if ``return_all`` is False, then return ``(True, m)``, where ``m``
            is the subgraph Morphism. If ``return_all`` is True, then return
            ``(True, iterator_of_morphisms)``.
          * If not, then always return``(False, None)``.

    Args:
       mhgraph1 (:obj:`MHGraph`): the domain mhgraph.
       mhgraph2 (:obj:`MHGraph`): the codomain mhgraph.
       return_all (:obj:`bool`): if False (default) return only one witeness Morphism,
          else return all.

    Return:
       * If ``mhgraph1`` is a subgraph of ``mhgraph2`` then return ``(True, m)`` or
         ``(True, iterator_of_morphisms)``, depending on the value of ``return_all``.
       * If ``mhgraph1`` is not a subgraph of ``mhgraph2``, then always return
         ``(False, None)``.
    """
    # Heuristic checks
    if any((len(vertices(mhgraph1)) > len(vertices(mhgraph2)),
            len(mhgraph1.keys()) > len(mhgraph2.keys()),
            sum(mhgraph1.values()) > sum(mhgraph2.values()))):
        # Failed heuristic checks. Not a subgraph.
        return False, None

    injective_vertexmaps = cast(Iterator[InjectiveVertexMap],
                                generate_vertexmaps(hgraph_from_mhgraph(mhgraph1),
                                                    hgraph_from_mhgraph(mhgraph2),
                                                    injective=True))

    morphisms: Iterator[Morphism]
    morphisms = filter(None, map(morphism, injective_vertexmaps))

    subgraph_morphisms: Iterator[Morphism]
    subgraph_morphisms = filter(lambda m: is_immediate_subgraph(graph_image(m, mhgraph1),
                                                                mhgraph2), morphisms)

    first_morphism: List[Morphism]
    first_morphism, subgraph_morphisms = mit.spy(subgraph_morphisms)
    if not first_morphism:
        # Not a subgraph.
        return False, None

    if return_all:
        return True, subgraph_morphisms
    # Return the only item in first_morphism.
    return True, mit.one(first_morphism)


def isomorphism_search(mhgraph1: MHGraph, mhgraph2: MHGraph, return_all: bool = False) \
        -> Tuple[bool, Union[None, Morphism, Iterator[Morphism]]]:
    """Brute-force isomorphism-search algorithm extended to MHGraphs.

    Use :obj:`subgraph_search()` twice to check if ``mhgraph1`` is isomorphic to
    ``mhgraph2``. A domain MHGraph and codomain MHGraph are `isomorphic` to each other if
    each is a subgraph of the other.

    Args:
       mhgraph1 (:obj:`MHGraph`): the domain mhgraph.
       mhgraph2 (:obj:`MHGraph`): the codomain mhgraph.
       return_all (:obj:`bool`): if False (default), then return only one witness
          isomorphism else return all.

    Return:
       If ``mhgraph1`` is indeed isomorphic to ``mhgraph2``, and if ``return_all`` is
       False, then return a ``(True, m)``, where ``m`` is an isomorphism.
       If ``return_all`` is True, then return ``(True, iterator_of_morphisms)``.
       If ``mhgraph1`` is not isomorphic to ``mhgraph2``, then return ``(False, None)``.
    """
    # Heuristic checks
    if any((len(vertices(mhgraph1)) != len(vertices(mhgraph2)),
            len(mhgraph1.keys()) != len(mhgraph2.keys()),
            sorted(mhgraph1.values()) != sorted(mhgraph2.values()))):
        # Not isomorphic.
        return False, None

    if not subgraph_search(mhgraph1=mhgraph2, mhgraph2=mhgraph1, return_all=False)[0]:
        # Not isomorphic. Probably an unreachable line.
        return False, None    # pragma: no cover
    return subgraph_search(mhgraph1, mhgraph2, return_all=return_all)


if __name__ == '__main__':
    logger.info(f'Running {__file__} as an independent script.')
    logger.info('We can perform an isomophism search as follows:')
    logger.info('>>> isomorphism_search(mhgraph([[1, 2, 3], [1, 2]]), '
                'mhgraph([[3, 2, 4], [2, 4]]))')
    logger.info(isomorphism_search(mhgraph([[1, 2, 3], [1, 2]]),
                                   mhgraph([[3, 2, 4], [2, 4]])))
    logger.info('>>> isomorphism_search(mhgraph([[1, 2, 3], [1, 2]]), '
                'mhgraph([[3, 2, 4], [2, 4]]),return_all=True)')
    logger.info(isomorphism_search(mhgraph([[1, 2, 3], [1, 2]]),
                                   mhgraph([[3, 2, 4], [2, 4]]),
                                   return_all=True))

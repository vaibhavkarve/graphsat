#!/usr/bin/env python3.8
"""Constructors and functions for Graph and MHGraph morphisms.

This includes an implementation of the brute-force subgraph search algorithm and a
brute-force isomorphism search algorithm for MHGraphs.
"""

import itertools as it
from typing import (AbstractSet, Callable, Dict, Iterable, Iterator, KeysView,
                    Mapping, NamedTuple, NewType, Optional, Tuple, TypeGuard, TypeVar,
                    Union, cast)

import more_itertools as mit
from loguru import logger

from graphsat.graph import Vertex
from graphsat.mhgraph import (HGraph, MHGraph, hgraph_from_mhgraph, mhgraph,
                              vertices)

# Types
# =====

#: `Translation` is an alias for ``dict[Vertex, Vertex]``.
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
    #assert set(ivmap.translation.keys()) <= vertices(mhg), \
    #    f'InjectiveVertexMap keys should be vertices of {mhg = }'
    mapped_mhgraph: list[list[Vertex]]
    mapped_mhgraph = [[ivmap.translation[vertex] for vertex in hedge]
                      for hedge in mhg.elements()]
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

    scheme = it.combinations if injective else it.combinations_with_replacement

    codomain: Iterator[Tuple[Vertex, ...]]
    codomain = scheme(vertices(hgraph2), len(vertices(hgraph1)))

    mappings1: Iterator[Tuple[Tuple[Vertex, ...], Tuple[Vertex, ...]]]
    mappings1 = it.product(domain, codomain)

    mappings2: Iterator[Iterator[Tuple[Vertex, Vertex]]]
    mappings2 = (zip(*pair) for pair in mappings1)

    translations: Iterator[Translation]
    translations = map(dict, mappings2)

    vertexmaps_optional: Iterator[Optional[VertexMap]]
    vertexmaps_optional = map(lambda t: vertexmap(t, hgraph1, hgraph2), translations)

    def vertexmaps_should_be_non_none() -> Iterator[VertexMap]:
        vertexmaps: Iterator[VertexMap]
        vertexmaps_none: Iterator[None]
        vertexmaps_none, vertexmaps = mit.partition(  # type: ignore
            lambda vm: vm is not None, vertexmaps_optional)
        assert not list(vertexmaps_none), 'All generated vertexmaps should have been non-None.'
        return vertexmaps

    vertexmaps = vertexmaps_should_be_non_none()
    if not injective:
        return vertexmaps

    inj_vertexmaps_optional: Iterator[Optional[InjectiveVertexMap]]
    inj_vertexmaps_optional = map(injective_vertexmap, vertexmaps)

    def inj_vertexmaps_should_be_non_none() -> Iterator[InjectiveVertexMap]:
        inj_vertexmaps: Iterator[InjectiveVertexMap]
        inj_vertexmaps_none: Iterator[None]
        inj_vertexmaps_none, inj_vertexmaps = mit.partition(  # type: ignore
            lambda vm: vm is not None, inj_vertexmaps_optional)
        assert not list(inj_vertexmaps_none), \
            'All generated inj-vertexmaps should have been non-None.'
        return inj_vertexmaps
    return inj_vertexmaps_should_be_non_none()


def is_immediate_subgraph(mhg1: MHGraph, mhg2: MHGraph) -> bool:
    """Check if the domain MHGraph is an immediate-subgraph of the codomain.

    We say that the domain MHGraph is an `immediate subgraph` of the codomain MHGraph if
    every HEdge in the domain MHGraph (with multiplicity ``m``) is in the codomain MHGraph
    with multiplicity no less than ``m``.

    Args:
       mhg1 (:obj:`MHGraph`)
       mhg2 (:obj:`MHGraph`)

    Return:
       ``True`` if every HEdge of ``mhg1`` with multiplicity ``m`` is a HEdge of
       ``mhg2`` with multiplicity no less than ``m``, else return ``False``.

    """
    return all(hedge in mhg2 and mult <= mhg2[hedge] for hedge, mult in mhg1.items())


def subgraph_search(mhg1: MHGraph, mhg2: MHGraph, return_all: bool) \
        -> Tuple[bool, None | Morphism | Iterator[Morphism]]:
    """Brute-force subgraph search algorithm extended to MHGraphs.

    ``mhg1`` is a `subgraph` of ``mhg2`` if there is a Morphism with domain HGraph
    as ``hgraph_from_mhgraph(mhg1)`` and codomain HGraph as
    ``hgraph_from_mhgraph(mhg2)`` such that every HEdge of ``mhg1`` maps to a
    unique HEdge (also accounting for multiplicities) of ``mhg2`` under the
    Translation dictionary.

    Algorithm:
       * First perform some heuristic checks
       * If the two MHGraphs pass the heuristic checks, then generate all Morphisms from
         ``hgraph_from_mhgraph(mhg1)`` to ``hgraph_from_mhgraph(mhg2)``.
       * Find the image of ``hgraph_from_mhgraph(mhg1)`` under each Morphism.
       * Check that each HEdge of the image HGraph is present with higher multiplicity in
         the codomain.
          * If yes, and if ``return_all`` is False, then return ``(True, m)``, where ``m``
            is the subgraph Morphism. If ``return_all`` is True, then return
            ``(True, iterator_of_morphisms)``.
          * If not, then always return``(False, None)``.

    Args:
       mhg1 (:obj:`MHGraph`): the domain mhgraph.
       mhg2 (:obj:`MHGraph`): the codomain mhgraph.
       return_all (:obj:`bool`): if False return only one witeness Morphism, else
          return all.

    Return:
       * If ``mhg1`` is a subgraph of ``mhg2`` then return ``(True, m)`` or
         ``(True, iterator_of_morphisms)``, depending on the value of ``return_all``.
       * If ``mhg1`` is not a subgraph of ``mhg2``, then always return
         ``(False, None)``.

    """
    heuristics: dict[str, Callable[[MHGraph], int]]
    heuristics = {'# vertices': lambda mhg: len(vertices(mhg)),
                  '# edges-no-mul': lambda mhg: len([h for h in mhg.keys() if len(h) == 2]),
                  '# hedges-no-mul': lambda mhg: len([h for h in mhg.keys() if len(h) == 3]),
                  '# edges': lambda mhg: len([h for h in mhg if len(h) == 2]),
                  '# hedges': lambda mhg: len([h for h in mhg if len(h) == 3])}
    if not all(value(mhg1) <= value(mhg2) for value in heuristics.values()):
        # Failed heuristic checks. Not a subgraph.
        return False, None

    hg1: HGraph = hgraph_from_mhgraph(mhg1)
    hg2: HGraph = hgraph_from_mhgraph(mhg2)
    injective_vertexmaps = cast(Iterator[InjectiveVertexMap],
                                generate_vertexmaps(hg1, hg2, injective=True))

    morphisms: Iterator[Morphism]
    morphisms = filter(None, map(morphism, injective_vertexmaps))

    subgraph_morphs: Iterator[Morphism]
    subgraph_morphs = filter(lambda m: is_immediate_subgraph(graph_image(m, mhg1),
                                                             mhg2), morphisms)

    first_morph: list[Morphism]
    first_morph, subgraph_morphs = mit.spy(subgraph_morphs)
    if not first_morph:
        # Not a subgraph.
        return False, None

    if return_all:
        return True, subgraph_morphs
    return True, mit.one(first_morph)


def isomorphism_search(mhg1: MHGraph, mhg2: MHGraph, return_all: bool = False) \
        -> Tuple[bool, Union[None, Morphism, Iterator[Morphism]]]:
    """Brute-force isomorphism-search algorithm extended to MHGraphs.

    Use :obj:`subgraph_search()` twice to check if ``mhg1`` is isomorphic to
    ``mhg2``. A domain MHGraph and codomain MHGraph are `isomorphic` to each other if
    each is a subgraph of the other.

    Args:
       mhg1 (:obj:`MHGraph`): the domain mhgraph.
       mhg2 (:obj:`MHGraph`): the codomain mhgraph.
       return_all (:obj:`bool`): if False (default), then return only one witness
          isomorphism else return all.

    Return:
       If ``mhg1`` is indeed isomorphic to ``mhg2``, and if ``return_all`` is
       False, then return a ``(True, m)``, where ``m`` is an isomorphism.
       If ``return_all`` is True, then return ``(True, iterator_of_morphisms)``.
       If ``mhg1`` is not isomorphic to ``mhg2``, then return ``(False, None)``.

    """
    is_subgraph, _ = subgraph_search(mhg1=mhg2, mhg2=mhg1, return_all=False)
    if not is_subgraph:
        return False, None
    return subgraph_search(mhg1, mhg2, return_all=return_all)


Elem = TypeVar('Elem')


def unique_upto_equiv(iterable: Iterable[Elem], equiv: Callable[[Elem, Elem], bool]) \
        -> Iterator[Elem]:
    """Remove elements of iterable that are equivalent to previous elements.

    Args:
       iterable (:obj:`Iterable[Elem]`): a iterable of any type (we call this type
          Elem).
       equiv (:obj:Callable[[Elem, Elem], Any]): an equivalence relation on type Elem.

    Return:
       An iterator without duplicates (under the equivalence relation).

    Complexity:
       The outer loop traverses at most `n` elements. The inner loop traverses:
       0 + 1 + 2 + ... + (n-1) = n(n-1)/2 element at most. Hence, total traversed
       elements = n + n(n-1)/2 = n(n+1)/2 ~ O(n^2).

    Usage:
       This can be called on a iterable of MHGraphs with `equiv=isomorphism_search`.

    Note:
       * This function might behave unpreductably if `equiv` is not an equivalence relation.
       * This function calls more_itertools.unique_everseen on iterable before processing
         it.  This removes any duplicates that can be identified by reflexivity.

    """
    seen: list[Elem] = []
    for element in mit.unique_everseen(iterable):
        equiv_to_seen: Iterator[bool]
        equiv_to_seen = (equiv(element, seen_element) for seen_element in seen)
        if not any(equiv_to_seen):
            seen.append(element)
            yield element


def unique_upto_isom(mhgraph_iterable: Iterable[MHGraph]) -> Iterator[MHGraph]:
    """Remove isomorphic duplicates of MHGraphs from the iterable."""
    def is_isomorphic(mhg1: MHGraph, mhg2: MHGraph) -> bool:
        return isomorphism_search(mhg1, mhg2, return_all=False)[0]
    return unique_upto_equiv(mhgraph_iterable, is_isomorphic)


if __name__ == '__main__':
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

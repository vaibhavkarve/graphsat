#!/usr/bin/env python3
"""All functions that work on Graphs, HGraphs and MHGraphs live here.

This includes an implementation of the brute-force subgraph search algorithm and a
brute-force isomorphism search algorithm for MHGraphs.
"""

import itertools as it
from typing import (AbstractSet, Callable, cast, Dict, FrozenSet,
                    Iterator, KeysView, Mapping, NamedTuple, NewType,
                    Optional, Tuple, Union)
from loguru import logger

from graph import graph, Graph, Vertex
from mhgraph import hgraph, HGraph, mhgraph, MHGraph, vertices

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


class NotASubgraphError(Exception):
    """Exception raised when a MHGraph is not a subgraph of another.

    Attributes:
        message -- explanation of the error

    """

    def __init__(self, message: Optional[str] = None) -> None:
        """Init method for the custom Exception."""
        super().__init__()
        self.message = message


# Conversion Functions
# ====================


def graph_from_mhgraph(mhgraph_instance: MHGraph) -> Graph:
    """Obtain a simple Graph from a MHGraph if possible. If not, raise a ValueError.

    A MHGraph can be converted to a simple Graph if:
    - it has no hyper-edges,
    - its edges have no multiplicities.

    Args:
       mhgraph_instance (:obj:`MHGraph`): a MHGraph which can be coerced to a
          simple graph.

    Return:
       A simple Graph with the same Edges as ``mhgraph_instance``, but with multiplicities
       removed.

    Raises:
       ValueError: if ``mhgraph_instance`` cannot be coerced to a simple graph.

    """
    if not all(multiplicity == 1 for multiplicity in mhgraph_instance.values()):
        raise ValueError('Multi-edges cannot be coerced to simple edges.')
    return graph(mhgraph_instance.keys())


def hgraph_from_mhgraph(mhgraph_instance: MHGraph) -> HGraph:
    """Obtain a HGraph by ignoring the HEdge-multiplicities of a hgraph.

    Args:
       mhgraph_instance (:obj:`MHGraph`)

    Return:
       A HGraph with the same HEdges as ``mhgraph_instance``, but with multiplicities
       removed.

    """
    return hgraph(mhgraph_instance.keys())


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
              hgraph2: Optional[HGraph] = None) -> VertexMap:
    """Check if a Translation is a VertexMap from one HGraph to another.

    A Translation is a `VertexMap` if its keys are **all** the Vertices of the domain
    HGraph and its values are **some** (or **all**) the Vertices of the codomain H

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
       A VertexMap named-tuple.

    Raises:
       ValueError: if not every Vertex of ``hgraph1`` is a key of ``translation``.
       ValueError: if the values of ``translation`` are not a subset of the Vertices of
          ``hgraph2``.

    """
    if hgraph2 is None:
        hgraph2 = hgraph1

    keys_are_all_vertices: bool
    keys_are_all_vertices = translation.keys() == vertices(hgraph1)

    values_are_some_vertices: bool
    values_are_some_vertices = set(translation.values()) <= vertices(hgraph2)

    if keys_are_all_vertices and values_are_some_vertices:
        return VertexMap(hgraph1=hgraph1,
                         hgraph2=hgraph2,
                         translation=dict(translation))
    raise ValueError('The given translation map does not satisfy VertexMap axioms.')


def injective_vertexmap(vmap: VertexMap) -> InjectiveVertexMap:
    """Check if a VertexMap is injective.

    A VertexMap is `injective` if its Translation dictionary is, i.e. if its translation
    has the same number of keys and values.

    Args:
       vmap (:obj:`VertexMap`): a VertexMap named-tuple.

    Return:
       ``vmap`` after casting to an InjectiveVertexMap named-tuple.

    Raises:
       ValueError: if ``vmap`` is not injective.

    """
    if len(vmap.translation.keys()) == len(frozenset(vmap.translation.values())):
        return InjectiveVertexMap(vmap)
    raise ValueError('The given VertexMap does not satisfy InjectiveVertexMap axioms.')


def graph_image(ivmap: InjectiveVertexMap, mhgraph_instance: MHGraph) -> MHGraph:
    """Return the image of a MHGraph under an InjectiveVertexMap.

    .. note::
       In the special case of ``ivmap.hgraph1 == hgraph_from_mhgraph(mhgraph_instance)``,
       this function is guaranteed to always return a valid MHGraph because:

       1. the axioms of VertexMap ensure that all Vertices of the domain MHGraph are
          mapped.
       2. the axioms of InjectiveVertexMap prevent repetition of a Vertex in any single
          HEdge of the image.
       3. the axioms of InjectiveVertexMap also imply that if the domain MHGraph has all
          HEdge-multiplicities equal to one, then so will the image mhgraph.

       However, for a more general ``mhgraph_instance``, there are no such guarantees.

    Args:
        ivmap (:obj:`InjectiveVertexMap`): an InjectiveVertexMap named-tuple.
        mhgraph_instance (:obj:`MHGraph`): the MHGraph to be translated/mapped.

    Return:
       A MHGraph formed by mapping the Vertices of ``mhgraph_instance`` using
       ``ivmap.translation``, while keeping the adjacency of Vertices of
       ``mhgraph_instance`` intact.

    """
    get_translation = cast(Callable[[Vertex], Vertex], ivmap.translation.get)

    mapped_mhgraph: Iterator[FrozenSet[Vertex]]
    mapped_mhgraph = map(lambda hedge: frozenset(map(get_translation, hedge)),
                         mhgraph_instance.elements())
    return mhgraph(list(mapped_mhgraph))


def morphism(ivmap: InjectiveVertexMap) -> Morphism:
    """Check if an InjectiveVertexMap is a Morphism.

    A `Morphism` (which is short for HGraph-homomophism) is an InjectiveVertexMap
    such that adjacent Vertices of the domain HGraph are mapped to adjacent vertices
    in the codomain H

    .. note::
       1. Injectivity ensures that HEdges do not get mapped to collapsed HEdges.
       2. Morphisms ignore HEdge-multiplicities.
       3. Not every InjectiveVertexMap is a Morphism.
       4. An empty dictionary is not a VertexMap translation and therefore not a Morphism
          translation.

    Args:
       ivmap (:obj:`InjectiveVertexMap`): an InjectiveVertexMap named-tuple.

    Return:
       ``ivmap`` cast as a Morphism named-tuple.

    Raises:
       ValueError: if a HEdge of ``ivmap.hgraph1`` gets mapped to a HEdge under
                   ``ivmap.translation`` that is not an HEdge of ``ivmap.hgraph2``.

    """
    mapped_hedges: KeysView[AbstractSet[Vertex]]
    mapped_hedges = graph_image(ivmap, mhgraph(ivmap.hgraph1)).keys()

    if all(hedge in ivmap.hgraph2 for hedge in mapped_hedges):
        return Morphism(ivmap)
    raise ValueError('The given InjectiveVertexMap does not satisfy Morphism axioms.')


# Higher (MH)Graph Operations
# ===========================


def generate_vertexmaps(hgraph1: HGraph,
                        hgraph2: Optional[HGraph],
                        injective: bool = True) -> Iterator[VertexMap]:
    """Generate all the (Injective)VertexMaps from domain HGraph to codomain HGraph.

    Args:
       hgraph1 (:obj:`HGraph`): the domain H
       hgraph2 (:obj:`HGraph`, optional): the codomain H If ``hgraph2`` is
          not provided, then generate all (Injective)VertexMaps from ``hgraph1`` to
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
    codomain = combinatorial_scheme(vertices(hgraph2),
                                    len(vertices(hgraph1)))

    mappings1: Iterator[Tuple[Tuple[Vertex, ...], Tuple[Vertex, ...]]]
    mappings1 = it.product(domain, codomain)

    mappings2: Iterator[Iterator[Tuple[Vertex, Vertex]]]
    mappings2 = (zip(*pair) for pair in mappings1)

    translations: Iterator[Translation]
    translations = map(dict, mappings2)

    def translation_to_vertexmap(translation: Translation) -> Optional[VertexMap]:
        try:
            return vertexmap(hgraph1=hgraph1, hgraph2=hgraph2, translation=translation)
        except ValueError:
            return None

    vertexmaps: Iterator[VertexMap]
    vertexmaps = filter(None, map(translation_to_vertexmap, translations))
    if not injective:
        return vertexmaps

    def vertexmap_to_injective(vmap: VertexMap) -> Optional[InjectiveVertexMap]:
        try:
            return injective_vertexmap(vmap)
        except ValueError:
            return None

    injective_vertexmaps: Iterator[InjectiveVertexMap]
    injective_vertexmaps = filter(None, map(vertexmap_to_injective, vertexmaps))
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


def subgraph_search(mhgraph1: MHGraph,
                    mhgraph2: MHGraph,
                    return_all: bool = False) -> Union[Morphism, Iterator[Morphism]]:
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
         the codomain  If yes, then return the Morphism (as it is the subgraph
         Morphism). If not, then raise a NotASubgraphError.

    Args:
       mhgraph1 (:obj:`MHGraph`): the domain mhgraph.
       mhgraph2 (:obj:`MHGraph`): the codomain mhgraph.

    Return:
       If ``mhgraph1`` is indeed the subgraph of ``mhgraph2``, then return a Morphism
       named-tuple with domain Graph ``graph_from_mhgraph(mhgraph1)``, codomain Graph
       ``graph_from_mhgraph(mhgraph2)`` and translation dictionary as the Translation that
       maps Vertices of ``mhgraph1`` into Vertices of ``mhgraph2``.

    Raises:
       NotASubgraphError - If ``mhgraph1`` is not a subgraph of ``mhgraph2``.

    """
    # Heuristic checks
    if any((len(vertices(mhgraph1)) > len(vertices(mhgraph2)),
            len(mhgraph1.keys()) > len(mhgraph2.keys()),
            sum(mhgraph1.values()) > sum(mhgraph2.values()))):
        raise NotASubgraphError(f'{mhgraph1} is not a subgraph of {mhgraph2}'
                                ' based on heuristic checks.')

    injective_vertexmaps = cast(Iterator[InjectiveVertexMap],
                                generate_vertexmaps(hgraph_from_mhgraph(mhgraph1),
                                                    hgraph_from_mhgraph(mhgraph2),
                                                    injective=True))

    def injective_vertexmap_to_morphism(ivmap: InjectiveVertexMap) -> Optional[Morphism]:
        try:
            return morphism(ivmap)
        except ValueError:
            return None

    morphisms: Iterator[Morphism]
    morphisms = filter(None, map(injective_vertexmap_to_morphism, injective_vertexmaps))

    subgraph_morphisms: Iterator[Morphism] \
        = filter(lambda m: is_immediate_subgraph(graph_image(m, mhgraph1),
                                                 mhgraph2), morphisms)
    if not return_all:
        try:
            return next(subgraph_morphisms)  # Return the first one, else raise Error
        except StopIteration:
            raise NotASubgraphError(f'{mhgraph1} is not a subgraph of {mhgraph2}')
    return subgraph_morphisms


def isomorphism_search(mhgraph1: MHGraph,
                       mhgraph2: MHGraph,
                       return_all: bool = False) -> Union[Morphism, Iterator[Morphism]]:
    """Brute-force isomorphism-search algorithm extended to MHGraphs.

    Use :obj:`subgraph_search()` twice to check if ``mhgraph1`` is isomorphic to
    ``mhgraph2``. A domain MHGraph and codomain MHGraph are `isomorphic` to each other if
    each is a subgraph of the other.

    Args:
       mhgraph1 (:obj:`MHGraph`): the domain mhgraph.
       mhgraph2 (:obj:`MHGraph`): the codomain mhgraph.

    Return:
       If ``mhgraph1`` is indeed isomorphic to ``mhgraph2``, then return a Morphism
       named-tuple with domain Graph ``graph_from_mhgraph(mhgraph1)``, codomain Graph
       ``graph_from_mhgraph(mhgraph2)`` and translation dictionary as the Translation that
       maps Vertices of ``mhgraph1`` into Vertices of ``mhgraph2``.

    Raises:
       NotASubgraphError - If ``mhgraph1`` is not isomorphic to ``mhgraph2``.

    """
    # Heuristic checks
    if any((len(vertices(mhgraph1)) != len(vertices(mhgraph2)),
            len(mhgraph1.keys()) != len(mhgraph2.keys()),
            sorted(mhgraph1.values()) != sorted(mhgraph2.values()))):
        raise NotASubgraphError(f'{mhgraph1} is not isomorphic to {mhgraph2}'
                                ' based on heuristic checks.')

    return subgraph_search(mhgraph1, mhgraph2, return_all) \
        or subgraph_search(mhgraph1=mhgraph2, mhgraph2=mhgraph1, return_all=return_all)


if __name__ == '__main__':
    logger.info(f'Running {__file__} as an independent script.')
    logger.info(f'We can perform an isomophism search as follows:')
    logger.info('>>> isomorphism_search(mhgraph([[1, 2, 3], [1, 2]]), '
                'mhgraph([[3, 2, 4], [2, 4]]))')
    logger.info(isomorphism_search(mhgraph([[1, 2, 3], [1, 2]]),
                                   mhgraph([[3, 2, 4], [2, 4]])))

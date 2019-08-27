#!/usr/bin/env python3
"""All functions that work on Graphs, HGraphs and MHGraphs live here.

This includes an implementation of the brute-force subgraph search algorithm and a
brute-force isomorphism search algorithm for MHGraphs.
"""

import itertools as it
from typing import (AbstractSet, Callable, cast, Dict, FrozenSet, Iterable, Iterator,
                    KeysView, Mapping, NamedTuple, NewType, Optional, Tuple, Union)
from loguru import logger  # type: ignore

import graph
import mhgraph

# Types
# =====

#: `Translation` is an alias for ``Dict[graph.Vertex, graph.Vertex]``.
Translation = Dict[graph.Vertex, graph.Vertex]

#: `VertexMap` is a `collections.NamedTuple` with three named entries --- a `domain` HGraph
#: (called ``hgraph1``), a `codomain` HGraph (called ``hgraph2``), and a Translation
#: dictionary (called ``translation``) between the Vertices of the two HGraphs.
VertexMap = NamedTuple('VertexMap', [('hgraph1', mhgraph.HGraph),
                                     ('hgraph2', mhgraph.HGraph),
                                     ('translation', Translation)])

InjectiveVertexMap = NewType('InjectiveVertexMap', VertexMap)
InjectiveVertexMap.__doc__ = """`InjectiveVertexMap` is a subtype of `VertexMap`."""

Morphism = NewType('Morphism', InjectiveVertexMap)
Morphism.__doc__ = """`Morphism` is a subtype of `InjectiveVertexMap`."""


# Conversion Functions
# ====================


def graph_from_mhgraph(mhgraph_instance: mhgraph.MHGraph) -> graph.Graph:
    """Obtain a simple Graph from a MHGraph if possible. If not, raise a ValueError.

    A mhgraph.MHGraph can be converted to a simple graph.Graph if:
    - it has no hyper-edges,
    - its edges have no multiplicities,
    - it does not have vertices that are both in vertex-pair-edges and single-vertex-edges.

    Args:
       mhgraph_instance (:obj:`mhgraph.MHGraph`): a MHGraph which can be coerced to a
          simple Graph.

    Return:
       A simple Graph with the same Edges as ``mhgraph_instance``, but with multiplicities
       removed.

    Raises:
       ValueError: if ``mhgraph_instance`` cannot be coerced to a simple Graph.

    """
    if not all(multiplicity == 1 for multiplicity in mhgraph_instance.values()):
        raise ValueError('Multi-edges cannot be coerced to simple edges.')
    return graph.graph(mhgraph_instance.keys())


def hgraph_from_mhgraph(mhgraph_instance: mhgraph.MHGraph) -> mhgraph.HGraph:
    """Obtain a HGraph by ignoring the HEdge-multiplicities of a MHGraph.

    Args:
       mhgraph_instance (:obj:`mhgraph.MHGraph`)

    Return:
       A HGraph with the same HEdges as ``mhgraph_instance``, but with multiplicities
       removed.
    """
    return mhgraph.hgraph(mhgraph_instance.keys())


def mhgraph_from_graph(graph_instance: graph.Graph) -> mhgraph.MHGraph:
    """Obtain a MHGraph from a Graph.

    Every graph.Graph is also a mhgraph.MHGraph (after some coercion).

    Args:
       graph_instance (:obj:`graph.Graph`)

    Return:
       A MHGraph whose HEdges are the Edges of ``graph_instance`` with HEdge-multiplicity
       one.
    """
    return mhgraph.mhgraph(graph_instance)


# Constructor Functions
# =====================


def vertexmap(translation: Mapping[graph.Vertex, graph.Vertex],
              hgraph1: mhgraph.HGraph,
              hgraph2: Optional[mhgraph.HGraph] = None) -> VertexMap:
    """Check if a Translation is a VertexMap from one HGraph to another.

    A Translation is a `VertexMap` if its keys are **all** the Vertices of the domain
    HGraph and its values are **some** (or **all**) the Vertices of the codomain HGraph.

    .. note::

       * The empty translation is never a VertexMap because a HGraph is not allowed to be
         empty.

    Args:
       translation (:obj:`Translation`): a Translation dict from all Vertices of ``hgraph1``
          to a subset of the Vertices of ``hgraph2``.
       graph1 (:obj:`mhgraph.HGraph`): the domain HGraph.
       graph2 (:obj:`mhgraph.HGraph`, optional): the codomain HGraph. If ``hgraph2`` is not
          provided, then check whether the given Translation is a
          VertexMap from ``hgraph1`` to itself.

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
    keys_are_all_vertices = translation.keys() == mhgraph.vertices(hgraph1)

    values_are_some_vertices: bool
    values_are_some_vertices = set(translation.values()) <= mhgraph.vertices(hgraph2)

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


def graph_image(ivmap: InjectiveVertexMap, mhgraph_instance: mhgraph.MHGraph) \
        -> mhgraph.MHGraph:
    """Return the image of a MHGraph under an InjectiveVertexMap.

    .. note::
       In the special case when ``ivmap.hgraph1 == hgraph_from_mhgraph(mhgraph_instance)``,
       this function is guaranteed to always return a valid MHGraph because:

       1. the axioms of VertexMap ensure that all Vertices of the domain MHGraph are mapped.
       2. the axioms of InjectiveVertexMap prevent repetition of a Vertex in any single
          HEdge of the image.
       3. the axioms of InjectiveVertexMap also imply that if the domain MHGraph has all
          HEdge-multiplicities euqal to one, then so will the image MHGraph.

       However, for a more general ``mhgraph_instace``, there are no such guarantees.

    Args:
        ivmap (:obj:`InjectiveVertexMap`): an InjectiveVertexMap named-tuple.
        mhgraph_instace (:obj:`mhgraph.MHGraph`): the MHGraph to be translated/mapped.

    Return:
       A MHGraph formed by mapping the Vertices of ``mhgraph_instace`` using
       ``ivmap.translation``, while keeping the adjacency of Vertices of ``mhgraph_instace``
       intact.
    """
    get_translation = cast(Callable[[graph.Vertex], graph.Vertex], ivmap.translation.get)

    mapped_mhgraph: Iterator[FrozenSet[graph.Vertex]]
    mapped_mhgraph = map(lambda hedge: frozenset(map(get_translation, hedge)),
                         mhgraph_instance.elements())
    return mhgraph.mhgraph(list(mapped_mhgraph))


def morphism(ivmap: InjectiveVertexMap) -> Morphism:
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
       ``ivmap`` cast as a Morphism named-tuple.

    Raises:
       ValueError: if a HEdge of ``ivmap.hgraph1`` gets mapped to a HEdge under
                   ``ivmap.translation`` that is not an HEdge of ``ivmap.hgraph2``.

    """
    mapped_hedges: KeysView[AbstractSet[graph.Vertex]]
    mapped_hedges = graph_image(ivmap, mhgraph.mhgraph(ivmap.hgraph1)).keys()

    if all(hedge in ivmap.hgraph2 for hedge in mapped_hedges):
        return Morphism(ivmap)
    raise ValueError('The given InjectiveVertexMap does not satisfy Morphism axioms.')


# Higher (MH)Graph Operations
# ===========================


def generate_vertexmaps(hgraph1: mhgraph.HGraph,
                        hgraph2: Optional[mhgraph.HGraph],
                        injective: bool = True) -> Iterator[VertexMap]:
    """Generate all the (Injective)VertexMaps from domain HGraph to codomain HGraph.

    Args:
       hgraph1 (:obj:`mhgraph.HGraph`): the domain HGraph.
       hgraph2 (:obj:`mhgraph.HGraph`, optional): the codomain HGraph. If ``hgraph2`` is
          not provided, then generate all (Injective)VertexMaps from ``hgraph1`` to itself.
       injective (:obj:`bool`, optional): if set to ``True`` (default), then generate all
          the InjectiveVertexMaps from ``hgraph1`` to ``hgraph2``. If set to ``False``,
          then generate all the VertexMaps from ``hgraph1`` to ``hgraph2``.

    Algorithm:
       * Set of (Injective)VertexMap from ``hgraph1`` to ``hgraph2`` is formed by taking
         the Cartesian product of the `Domain` and `Codomain`.
       * Here, the `Domain` consists of all permutations of the Vertices of the domain
         HGraph (i.e. the order matters in the Domain).
       * The `Codomain` consists of all combinations (without or with replacement, if
         ``injective`` is ``True` or ``False`` respectively) of the Vertices of the codomain
         HGraph (i.e. the order does not matter in the Codomain).

    Return:
       An Iterator of (Injective)VertexMaps from ``hgraph1`` to ``hgraph2``.
    """
    if hgraph2 is None:
        hgraph2 = hgraph1

    domain: Iterator[Tuple[graph.Vertex, ...]]
    domain = it.permutations(mhgraph.vertices(hgraph1))

    combinatorial_scheme = it.combinations if injective else it.combinations_with_replacement

    codomain: Iterable[Tuple[graph.Vertex, ...]]
    codomain = combinatorial_scheme(mhgraph.vertices(hgraph2), len(mhgraph.vertices(hgraph1)))

    mappings1: Iterator[Tuple[Tuple[graph.Vertex, ...], Tuple[graph.Vertex, ...]]]
    mappings1 = it.product(domain, codomain)

    mappings2: Iterator[Iterator[Tuple[graph.Vertex, graph.Vertex]]]
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


def is_immediate_subgraph(mhgraph1: mhgraph.MHGraph, mhgraph2: mhgraph.MHGraph) -> bool:
    """Check if the domain MHGraph is an immediate-subgraph of the codomain MHGraph.

    We say that the domain MHGraph is an `immediate subgraph` of the codomain MHGraph if
    every HEdge in the domain MHGraph (with multiplicity ``m``) is in the codomain MHGraph
    with multiplicity no less than ``m``.

    Args:
       mhgraph1 (:obj:`mhgraph.MHGraph`)
       mhgraph2 (:obj:`mhgraph.MHGraph`)

    Return:
       ``True`` if every HEdge of ``mhgraph1`` with multiplicity ``m`` is a HEdge of
       ``mhgraph2`` with multiplicity no less than ``m``, else return ``False``.
    """
    return all(hedge in mhgraph2 and mult <= mhgraph2[hedge]
               for hedge, mult in mhgraph1.items())


def subgraph_search(mhgraph1: mhgraph.MHGraph, mhgraph2: mhgraph.MHGraph) \
        -> Union[Morphism, bool]:
    """Brute-force subgraph search algorithm extended to MHGraphs.

    ``mhgraph1`` is a `subgraph` of ``mhgraph2`` if there is a Morphism with domain HGraph
    as ``hgraph_from_mhgraph(mhgraph1)`` and codomain HGraph as
    ``hgraph_from_mhgraph(mhgraph2)`` such that every HEdge of ``mhgraph1`` maps to a
    unique HEdge (also accounting for multiplicities) of ``mhgraph2`` under the Translation
    dictionary.

    Algorithm:
       * First perform some heuristic checks
       * If the two MHGraphs pass the heuristic checks, then generate all Morphisms from
         ``hgraph_from_mhgraph(mhgraph1)`` to ``hgraph_from_mhgraph(mhgraph2)``.
       * Find the image of ``hgraph_from_mhgraph(mhgraph1)`` under each Morphism.
       * Check that each HEdge of the image HGraph is present with higher multiplicity in
         the codomain MHGraph. If yes, then return the Morphism (as it is the subgraph
         Morphism). If not, then return ``False``.

    Args:
       mhgraph1 (:obj:`mhgraph.MHGraph`): the domain MHGraph.
       mhgraph2 (:obj:`mhgraph.MHGraph`): the codomain MHGraph.

    Return:
       If ``mhgraph1`` is indeed the subgraph of ``mhgraph2``, then return a Morphism
       named-tuple with domain Graph ``graph_from_mhgraph(mhgraph1)``, codomain Graph
       ``graph_from_mhgraph(mhgraph2)`` and translation dictionary as the Translation that
       maps Vertices of ``mhgraph1`` into Vertices of ``mhgraph2``.

       If ``mhgraph1`` is not a subgraph of ``mhgraph2``, then return ``False``.
    """
    # Heuristic checks
    if any([len(mhgraph.vertices(mhgraph1)) > len(mhgraph.vertices(mhgraph2)),
            len(mhgraph1.keys()) > len(mhgraph2.keys()),
            sum(mhgraph1.values()) > sum(mhgraph2.values())]):
        return False

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
        = filter(lambda morph: is_immediate_subgraph(graph_image(morph, mhgraph1), mhgraph2),
                 morphisms)
    return next(subgraph_morphisms, False)  # Return the first one, else return False


def isomorphism_search(mhgraph1: mhgraph.MHGraph, mhgraph2: mhgraph.MHGraph) \
        -> Union[Morphism, bool]:
    """Brute-force isomorphism-search algorithm extended to MHGraphs.

    Use :obj:`subgraph_search()` twice to check if ``mhgraph1`` is isomorphic to ``mhgraph2``.
    A domain MHGraph and codomain MHGraph are `isomorphic` to each other if each is a
    subgraph of the other.

    Args:
       mhgraph1 (:obj:`mhgraph.MHGraph`): the domain MHGraph.
       mhgraph2 (:obj:`mhgraph.MHGraph`): the codomain MHGraph.

    Return:
       If ``mhgraph1`` is indeed isomorphic to ``mhgraph2``, then return a Morphism
       named-tuple with domain Graph ``graph_from_mhgraph(mhgraph1)``, codomain Graph
       ``graph_from_mhgraph(mhgraph2)`` and translation dictionary as the Translation that
       maps Vertices of ``mhgraph1`` into Vertices of ``mhgraph2``.

       If ``mhgraph1`` is not isomorphic to ``mhgraph2``, then return ``False``.
    """
    # Heuristic checks
    if any([len(mhgraph.vertices(mhgraph1)) != len(mhgraph.vertices(mhgraph2)),
            len(mhgraph1.keys()) != len(mhgraph2.keys()),
            sorted(mhgraph1.values()) != sorted(mhgraph2.values())]):
        return False

    return subgraph_search(mhgraph1, mhgraph2) or subgraph_search(mhgraph2, mhgraph1)


if __name__ == '__main__':
    logger.info(f'Running {__file__} as an independent script.')
    logger.info(f'We can perform an isomophism search as follows:')
    logger.info('>>> isomorphism_search(mhgraph.mhgraph([[1, 2, 3], [1, 2]]), '
                'mhgraph.mhgraph([[3, 2, 4], [2, 4]]))')
    logger.info(isomorphism_search(mhgraph.mhgraph([[1, 2, 3], [1, 2]]),
                                   mhgraph.mhgraph([[3, 2, 4], [2, 4]])))

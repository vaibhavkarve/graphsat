#!/usr/bin/env python3
"""Constructors and functions for Loopless-Multi-Hyper-Graphs.

.. _definitionofagraph:

Definition of a Loopless-Multi-Hyper-Graph
==========================================
Throughout this module, we will take the term *MHGraph* to refer to mathematical objects
with the following properties:

   - All simple graphs (as laid out on the graph.py module) are MHGraphs.
   - Hyper-edges (referred to simply as an HEdge) are allowed, meaning that an can join
     more than two vertices together.
   - Multi-edges are allowed, meaning that each HEdge comes with a non-negative multiplicity:
      - multiplicity one HEdges are called simple edges.
      - multiplicity zero HEdges are simply ignored.
   - Multi-hyper-edges are allowed (meaning hyper-edges can also have multiplicities).
   - Isolated vertices are allowed.
   - Collapsed edges are not allowed, meaning an edge can be incident on a given vertex
     only once.
   - This also implies that looped-edges are not allowed, i.e. each edge must be
     incident on at least two distinct vertices.

Special note:

   In the graph.py module, special care was taken to prevent any vertices from appearing
   in both single-vertex-edges as well as vertex-pair-edges. This restriction is lifted in
   case of MHGraphs.

A *HGraph* is a MHGraph without HEdge-multiplicities.

"""

from collections import Counter as counter
from typing import (AbstractSet, cast, Collection, Counter, Dict, FrozenSet, List, NewType,
                    TypeVar, Union)
from loguru import logger  # type: ignore[import]

import graph


# PreMHGraph (Hashable Counter) for Storing MHGraphs
# ==================================================
# (for internal use only, partially documented)

#: ``T = TypeVar('T')``, i.e. ``T`` is a type variable.
T = TypeVar('T')  # pylint: disable=invalid-name


class PreMHGraph(Counter[AbstractSet[T]]):
    """`PreMHGraph[_T]` is a subclass of `collections.Counter[AbstractSet[_T]]`.

    It overrides Counter's ``__hash__`` and ``__repr__`` method, making it hashable.

    Implementation inspired by Raymond Hettinger's
    `solution <https://stackoverflow.com/questions/1151658/python-hashable-dicts>`_.
    Implementing ``__hash__`` enables us to put it inside containers like `Dict` or `Set`.

    """

    def __hash__(self) -> int:  # type: ignore[override]
        """Hash function that depends only on the keys of the Counter, ignoring values."""
        return hash(frozenset(self))

    def __repr__(self) -> str:
        """Print the PreMHGraph in a compact way."""
        unicode_superscripts: Dict[int, str]
        unicode_superscripts = {1: '\u00b9', 2: '\u00b2', 3: '\u00b3', 4: '\u2074',
                                5: '\u2075', 6: '\u2076', 7: '\u2077', 8: '\u2078',
                                9: '\u2079'}

        def hedge_string(hedge_: List[T]) -> str:
            return '(' + ','.join(map(str, hedge_)) + ')'

        def superscript(hedge_: List[T]) -> str:
            multiplicity: int = super(PreMHGraph, self).get(frozenset(hedge_), 0)
            return unicode_superscripts.get(multiplicity, f'^{multiplicity}')

        ordered_hedges: List[List[T]]
        ordered_hedges = sorted(sorted([sorted(hedge) for hedge in super().keys()]), key=len)

        hedge_strings: List[str]
        hedge_strings = [hedge_string(hedge) + superscript(hedge) for hedge in ordered_hedges]

        return ','.join(hedge_strings)


# Classes and Types
# =================

HEdge = NewType('HEdge', FrozenSet[graph.Vertex])
HEdge.__doc__ = """`HEdge` is a subtype of `FrozenSet[graph.Vertex]`."""

HGraph = NewType('HGraph', graph.PreGraph[graph.Vertex])
HGraph.__doc__ = """`HGraph` is a subtype of `graph.PreGraph[graph.Vertex]`."""

MHGraph = NewType('MHGraph', PreMHGraph[graph.Vertex])
MHGraph.__doc__ = """`MHGraph` is a subtype of `PreMHGraph[graph.Vertex]`."""


# Constructor Functions
# =====================


def hedge(vertex_collection: Collection[int]) -> HEdge:
    """Constructor-function for HEdge type.

    For definition of HEdge, refer to :ref:`definitionofagraph`.
    This function is idempotent.

    Args:
       vertex_collection (:obj:`Collection[int]`): a nonempty collection (list, tuple, set,
          or frozenset) of Vertices.

    Return:
       Check that each element satisfies the axioms for being a graph.Vertex.
       If yes, then cast to HEdge.

    Raises:
       ValueError: If ``vertex collection`` is an empty collection.

    """
    if not vertex_collection:
        raise ValueError(f'Encountered empty input {vertex_collection}')
    return HEdge(frozenset(map(graph.vertex, vertex_collection)))


def hgraph(hedge_collection: Collection[Collection[int]]) -> HGraph:
    """Constructor-function for HGraph type.

    A HGraph, is a MHGraph without HEdge-multiplicities.
    This function is idempotent.

    Args:
       hedge_collection (:obj:`Collection[Collection[int]]`): a nonempty collection (counter,
          list, tuple, set, or frozenset) of nonempty collections of Vertices.

    Return:
       If each element of the collection satisfies the axioms for being a HEdge, then the
       input is cast as a graph.PreGraph and then a HGraph.

    Raises:
       ValueError: If ``edge_collection`` is an empty collection.

    """
    if not hedge_collection:
        raise ValueError(f'Encountered empty input {hedge_collection}')
    return HGraph(graph.PreGraph(set(map(hedge, hedge_collection))))


def mhgraph(edge_collection: Collection[Collection[int]]) -> MHGraph:
    """Constructor-function for MHGraph type.

    For definition of a MHGraph, refer to :ref:`definitionofagraph`.
    This function is idempotent.

    Args:
       edge_collection (obj:`Collection[Collection[int]]`): a nonempty collection (counter,
          list, tuple, set, or frozenset) of nonempty collections of Vertices.

    Return:
       If ``edge_collections`` is a Counter, then this function takes HEdge-multiplicities
       into account (values of the Counter). If each element of the collection satisfies
       the axioms for being an HEdge, then the input is cast as a PreMHGraph and then a
       MHGraph.

    Raises:
       ValueError: If ``edge_collection`` is an empty collection.

    """
    if not edge_collection:
        raise ValueError(f'Encountered empty input {edge_collection}')

    if hasattr(edge_collection, 'elements'):
        # edge_collection is a Counter.
        edge_collection = cast(Counter[Collection[graph.Vertex]], edge_collection)
        return MHGraph(PreMHGraph(map(hedge, edge_collection.elements())))
    # edge_collection is not a Counter.
    return MHGraph(PreMHGraph(map(hedge, edge_collection)))


# Basic Functions
# ===============


def vertices(mhgraph_instance: Union[HGraph, MHGraph]) -> FrozenSet[graph.Vertex]:
    """Return a `frozenset` of all vertices of a MHGraph."""
    return frozenset.union(*mhgraph_instance)


def degree(vertex: graph.Vertex, mhgraph_instance: MHGraph) -> int:
    """Return the degree of a ``vertex`` in a MHGraph.

    This counts multiplicities.
    """
    return sum([multiplicity for hedge, multiplicity in mhgraph_instance.items()
                if vertex in hedge])


if __name__ == '__main__':
    logger.info(f'Running {__file__} as a stand-alone script.')
    logger.info('MHGraphs can be constructed using the mhgraph() function.')
    logger.info('>>> mhgraph([[1, 2, 3], [1, 2], [2, 3], [3, 1], [3, 2]])')
    logger.info(mhgraph([[1, 2, 3], [1, 2], [2, 3], [3, 1], [3, 2]]))
    logger.info('\n')
    logger.info('Or by passing a counter of HEdge-strings to the mhgraph() function.')
    logger.info('>>> mhgraph(counter({(1, 2, 3): 1, (1, 2): 1, (2, 3): 2, (3, 1): 1}))')
    logger.info(mhgraph(counter({(1, 2, 3): 1, (1, 2): 1, (2, 3): 2, (3, 1): 1})))
    logger.info('\n')
    logger.info('Given a MHGraph, we can get its vertices using the vertices() function.')
    logger.info('>>> vertices(mhgraph([[1, 2], [3, 1, 12]]))')
    logger.info(vertices(mhgraph([[1, 2], [3, 1, 12]])))
    logger.info('\n')
    logger.info('The degree() function returns the degree of a vertex in a MHGraph.')
    logger.info('>>> degree(2, mhgraph([[1, 2], [3, 1, 2], [1, 2]]))')
    logger.info(degree(graph.Vertex(2), mhgraph([[1, 2], [3, 1, 2], [1, 2]])))
    logger.info('\n')

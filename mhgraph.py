#!/usr/bin/env python3.9
"""Constructors and functions for Loopless-Multi-Hyper-Graphs.

.. _definitionofagraph:

Definition of a Loopless-Multi-Hyper-Graph
==========================================
Throughout this module, we will take the term *MHGraph* to refer to mathematical objects
with the following properties:

   - All simple graphs (as laid out on the graph.py module) are MHGraphs.
   - Hyper-edges (referred to simply as an HEdge) are allowed, meaning that an can join
     more than two vertices together.
   - Multi-edges are allowed, meaning that each HEdge comes with a non-negative
     multiplicity:
      - multiplicity one HEdges are called simple edges.
      - multiplicity zero HEdges are simply ignored.
   - Multi-hyper-edges are allowed (meaning hyper-edges can also have multiplicities).
   - Isolated vertices are allowed (single-vertex-edge are allowed -- think of these as
     self-loops).
   - Collapsed edges are not allowed, meaning an edge can be incident on a given vertex
     only once.

A *HGraph* is a MHGraph without HEdge-multiplicities.
"""
# Imports from standard library.
from collections import Counter as counter
from typing import AbstractSet, Collection, Counter, NewType, TypeVar, Union
# Imports from third-party modules.
from loguru import logger
# Imports from local modules.
import graph


# MHGraphType (Hashable Counter) for Storing MHGraphs
# ===================================================
# (for internal use only, partially documented)

#: ``T = TypeVar('T')``, i.e. ``T`` is a type variable.
T = TypeVar('T')  # pylint: disable=invalid-name


class MHGraphType(Counter[AbstractSet[T]]):
    """`MHGraphType[_T]` is a subclass of `collections.Counter[AbstractSet[_T]]`.

    It overrides Counter's ``__hash__`` and ``__repr__`` method, making it hashable.

    Implementation inspired by Raymond Hettinger's
    `solution <https://stackoverflow.com/questions/1151658/python-hashable-dicts>`_.
    Implementing ``__hash__`` enables us to put it inside containers like `Dict` or `Set`.

    """

    def __hash__(self) -> int:  # type: ignore
        """Hash function that depends only on the keys of the Counter, ignoring values."""
        return hash(frozenset(self))

    def __repr__(self) -> str:
        """Print the MHGraphType in a compact way."""
        unicode_superscripts: dict[int, str]
        unicode_superscripts = {1: '\u00b9', 2: '\u00b2', 3: '\u00b3', 4: '\u2074',
                                5: '\u2075', 6: '\u2076', 7: '\u2077', 8: '\u2078',
                                9: '\u2079'}

        ordered_hedges: list[AbstractSet[T]]
        ordered_hedges = sorted(sorted(super().keys()), key=len)  # pylint: disable=no-member

        def superscript(hedge_: AbstractSet[T]) -> str:
            multiplicity: int = super(MHGraphType, self).get(frozenset(hedge_), 0)
            return unicode_superscripts.get(multiplicity, f'^{multiplicity}')

        hedge_strings: list[str]
        hedge_strings = [str(h) + superscript(h) for h in ordered_hedges]

        return ','.join(hedge_strings)


class HEdge(frozenset[graph.Vertex]):  # pylint: disable=too-few-public-methods
    """`HEdge` is a subclass of `FrozenSet[graph.Vertex]`."""
    def __repr__(self) -> str:
        """Pretty-print the HEdge in a compact way."""
        return '(' + ', '.join(map(str, sorted(self))) + ')'



# Classes and Types
# =================

HGraph = NewType('HGraph', graph.GraphType[graph.Vertex])
HGraph.__doc__ = """`HGraph` is a subtype of `graph.PreGraph[graph.Vertex]`."""

class MHGraph(MHGraphType[graph.Vertex]):  # pylint: disable=too-few-public-methods
    """`MHGraph` is a subclass of `MHGraphType[graph.Vertex]`."""


# Constructor Functions
# =====================


def hedge(vertex_collection: Collection[int]) -> HEdge:
    """Constructor-function for HEdge type.

    For definition of HEdge, refer to :ref:`definitionofagraph`.
    This function is idempotent.

    Args:
       vertex_collection (:obj:`Collection[int]`): a nonempty collection (list, tuple,
          set, or frozenset) of Vertices.

    Return:
       Check that each element satisfies the axioms for being a graph.Vertex.
       If yes, then cast to HEdge.

    Raises:
       ValueError: If ``vertex_collection`` is an empty collection.

    """
    if not vertex_collection:
        raise ValueError(f'Encountered empty input {list(vertex_collection)}')
    return HEdge(frozenset(map(graph.vertex, vertex_collection)))


def hgraph(hedge_collection: Collection[Collection[int]]) -> HGraph:
    """Constructor-function for HGraph type.

    A HGraph, is a MHGraph without HEdge-multiplicities.
    This function is idempotent.

    Args:
       hedge_collection (:obj:`Collection[Collection[int]]`): a nonempty collection
          (counter, list, tuple, set, or frozenset) of nonempty collection of Vertices.

    Return:
       If each element of the collection satisfies the axioms for being a HEdge, then the
       input is cast as a graph.PreGraph and then a HGraph.

    Raises:
       ValueError: If ``hedge_collection`` is an empty collection.

    """
    if not hedge_collection:
        raise ValueError(f'Encountered empty input {hedge_collection}')
    return HGraph(graph.GraphType(set(map(hedge, hedge_collection))))


def mhgraph(edge_collection: Collection[Collection[int]]) -> MHGraph:
    """Constructor-function for MHGraph type.

    For definition of a MHGraph, refer to :ref:`definitionofagraph`.
    This function is idempotent.

    Args:
       edge_collection (obj:`Collection[Collection[int]]`): a nonempty Collection
          (counter, list, tuple, set, or frozenset) of nonempty collections of Vertices.

    Return:
       If ``edge_collection`` is a Counter, then this function takes HEdge-multiplicities
       into account (values of the Counter). If each element of the collection satisfies
       the axioms for being an HEdge, then the input is cast as a MHGraphType and then a
       MHGraph.

    Raises:
       ValueError: If ``edge_collection`` is an empty collection.

    """
    if not edge_collection:
        raise ValueError(f'Encountered empty input {list(edge_collection)}')

    try:
        # edge_collection is a Counter.
        return MHGraph(MHGraphType(map(hedge, edge_collection.elements())))  # type: ignore
    except AttributeError:
        # edge_collection is not a Counter.
        return MHGraph(MHGraphType(map(hedge, edge_collection)))


# Basic Functions
# ===============


def vertices(mhg: Union[HGraph, MHGraph]) -> frozenset[graph.Vertex]:
    """Return a `frozenset` of all vertices of a MHGraph."""
    return frozenset.union(*mhg)


def degree(vertex: graph.Vertex, mhg: MHGraph) -> int:
    """Return the degree of a ``vertex`` in a MHGraph.

    This counts multiplicities.
    """
    return sum([multiplicity for hedge, multiplicity in mhg.items()
                if vertex in hedge])


def pick_max_degree_vertex(mhg: MHGraph) -> graph.Vertex:
    """Pick vertex of highest degree."""
    degree_sequence: dict[graph.Vertex, int]
    degree_sequence = {v: degree(v, mhg) for v in vertices(mhg)}
    return max(degree_sequence, key=degree_sequence.get)


def pick_min_degree_vertex(mhg: MHGraph) -> graph.Vertex:
    """Pick vertex of lowest degree."""
    degree_sequence: dict[graph.Vertex, int]
    degree_sequence = {v: degree(v, mhg) for v in vertices(mhg)}
    return min(degree_sequence, key=degree_sequence.get)


def star(mhg: MHGraph, vertex: graph.Vertex) -> tuple[HEdge, ...]:
    """Return the tuple of all HEdges in ``mhg`` incident at ``vertex``."""
    assert vertex in vertices(mhg), f'{vertex} not of vertex of {mhg}'
    return tuple(hedge(h) for h in mhg.elements() if vertex in h)


def link(mhg: MHGraph, vertex: graph.Vertex) -> tuple[HEdge, ...]:
    """Return the link of ``mhg`` at ``vertex``.

    This is the star projected away from ``vertex``.

    """
    return tuple(hedge(set(h) - {vertex}) for h in star(mhg, vertex)
                 if set(h) != {vertex})


def sphr(mhg: MHGraph, vertex: graph.Vertex) -> tuple[HEdge, ...]:
    """Return the list of all HEdges in ``mhg`` *not* incident at ``vertex``."""
    return tuple(hedge(h) for h in mhg.elements() if vertex not in h)


def graph_union(mhg1: tuple[HEdge, ...], mhg2: tuple[HEdge, ...]) -> MHGraph:
    """Union of the two graphs."""
    assert mhg1 or mhg2, f'Encountered empty input {mhg1 = } or {mhg2 = }'
    return mhgraph(mhg1 + mhg2)


# Conversion Functions
# ====================


def graph_from_mhgraph(mhg: MHGraph) -> graph.Graph:
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
    return graph.graph(mhg.keys())


def hgraph_from_mhgraph(mhg: MHGraph) -> HGraph:
    """Obtain a HGraph by ignoring the HEdge-multiplicities of a hgraph.

    Args:
       mhg (:obj:`MHGraph`)

    Return:
       A HGraph with the same HEdges as ``mhg``, but with multiplicities
       removed.

    """
    return hgraph(mhg.keys())


def mhgraph_from_graph(graph_instance: graph.Graph) -> MHGraph:
    """Obtain a MHGraph from a mhgraph.

    Every Graph is also a MHGraph (after some coercion).

    Args:
       graph_instance (:obj:`Graph`)

    Return:
       A MHGraph whose HEdges are the Edges of ``graph_instance`` with HEdge-multiplicity
       one.

    """
    return mhgraph(graph_instance)


if __name__ == '__main__':
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

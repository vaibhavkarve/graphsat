#!/usr/bin/env python3.9
"""Constructors and functions for simple graphs.

.. _definitionofagraph:

Definition of a Simple Graph
============================
Throughout this module, we will take the term *Graph* to refer to mathematical objects
with the following properties:

   - A Graph is a set of edges.
   - There are only two kinds of edges allowed:
        + edges incident on exactly one vertex, i.e. single-vertex-edges,
          i.e. self loops.
        + edges incident on exactly two vertices, i.e. vertex-pair-edges.
   - Isolated vertices are allowed. (Not to be confused with a single-vertex-edge).
   - Edges do not have a directionality.
   - Edges do not have a multiplicity.
"""
# Imports from standard library.
from typing import Collection, NewType, TypeVar
# Importing third-party modules.
from loguru import logger


# GraphType for Storing Graphs
# ============================
# (for internal use only, partially documented)

#: ``T = TypeVar('T')``, i.e. ``T`` is a type varia
T = TypeVar('T')  # pylint: disable=invalid-name


class GraphType(set[Collection[T]]):  # pylint: disable=too-few-public-methods
    """`GraphType[_T]` is a subclass of `Set[Collection[_T]]`.

    It overrides the ``__repr__`` method.
    """

    def __repr__(self) -> str:
        """Print the GraphType in a compact way."""
        def edge_string(edge_instance: Collection[T]) -> str:
            return '(' + ','.join(map(str, sorted(edge_instance))) + ')'

        return ','.join(sorted(sorted(map(edge_string, self)), key=len))


# Classes and Types
# =================

Vertex = NewType('Vertex', int)
Vertex.__doc__ = """`Vertex` is a subtype of `int`."""

Edge = NewType('Edge', frozenset[Vertex])
Edge.__doc__ = """`Edge` is a subtype of `FrozenSet[Vertex]`."""

Graph = NewType('Graph', GraphType[Vertex])
Graph.__doc__ = """`Graph` is a subtype of `GraphType[Vertex]`."""


# Constructor Functions
# =====================


def vertex(positive_int: int) -> Vertex:
    """Constructor-function for Vertex type.

    By definition, a `Vertex` is simply a positive integer.
    This function is idempotent.

    Args:
       positive_int (:obj:`int`)

    Return:
       If input is indeed positive, then return ``positive_int`` after casting to Vertex.

    Raises:
       ValueError: If ``positive_int <= 0``.

    """
    if positive_int <= 0:
        raise ValueError('Vertices should be positive integers.')
    return Vertex(positive_int)


def edge(vertex_collection: Collection[int]) -> Edge:
    """Constructor-function for Edge type.

    For definition of an Edge, refer to :ref:`definitionofagraph`.
    This function is idempotent.

    Args:
       vertex_collection (:obj:`Collection[int]`): a collection (list, tuple, set, or
          frozenset) (of size one or two) of Vertices.

    Return:
       Check that each element satisfies the axioms for being a Vertex. If yes, then cast
       to Edge.

    Raises:
       ValueError: If ``vertex_collection`` is an empty collection.
       ValueError: If ``vertex_collection`` has more than two elements.

    """
    if not vertex_collection:
        raise ValueError(f'Encountered empty input {vertex_collection}')
    if len(vertex_collection) > 2:
        raise ValueError(f'Encountered a hyperedge in {vertex_collection}. '
                         'Use MHGraphs instead.')
    return Edge(frozenset(map(vertex, vertex_collection)))


def graph(edge_collection: Collection[Collection[int]]) -> Graph:
    """Constructor-function for Graph type.

    For definition of a Graph, refer to :ref:`definitionofagraph`.
    This function is idempotent.

    Args:
       edge_collection (obj:`Collection[Collection[int]]`): a nonempty collection
          (counter, list, tuple, set, frozenset) of nonempty collections (of length
          one or two) of Vertices.

    Return:
       If each element of the collection satisfies the axioms for being an Edge, then the
       input is cast as a GraphType and then a Graph.

    Raises:
       ValueError: If ``edge_collection`` is an empty collection.

    """
    if not edge_collection:
        raise ValueError(f'Encountered empty input {list(edge_collection)}')

    edges: set[Edge] = set(map(edge, edge_collection))
    return Graph(GraphType(edges))


# Basic Functions
# ===============


def vertices(graph_instance: Graph) -> frozenset[Vertex]:
    """Return a `frozenset` of all vertices of a Graph.

    Args:
       graph_instance (:obj:`Graph`)

    Return:
       A frozenset of all Vertices that any Edge of ``graph_instance`` is incident on.

    """
    return frozenset.union(*graph_instance)


if __name__ == '__main__':
    logger.info('Simple graphs can be constructed using the graph() function.')
    logger.info('This function gets rid of duplicate edges.')
    logger.info('>>> graph([[1, 2], [1, 2], [2, 3], [3, 1], [3, 2]])')
    logger.info(graph([[1, 2], [1, 2], [2, 3], [3, 1], [3, 2]]))
    logger.info('\n')
    logger.info('Given a Graph, we can get its set of vertices using vertices().')
    logger.info('>>> vertices(graph([[1, 2], [3, 1]]))')
    logger.info(vertices(graph([[1, 2], [3, 1]])))

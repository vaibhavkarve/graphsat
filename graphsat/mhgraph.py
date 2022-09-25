#!/usr/bin/env python3.8
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

An *HGraph* is a MHGraph without HEdge-multiplicities.
"""
from __future__ import annotations

from collections import Counter as counter
from typing import Collection, Counter, Iterable, NoReturn, Sequence
from typing_extensions import reveal_type

import anytree as at
from loguru import logger

from graphsat.graph import Graph, Vertex, graph, vertex

# Classes and Types
# =================

class HEdge(frozenset[Vertex]):  # pylint: disable=too-few-public-methods
    """`HEdge` is a subclass of `frozenset[Vertex]`."""
    def __repr__(self) -> str:
        """Pretty-print the HEdge in a compact way."""
        return '(' + ', '.join(map(str, sorted(self))) + ')'


class HGraph(frozenset[HEdge]):
    ...


class MHGraph(counter[HEdge]):
    def __hash__(self) -> int:  # type: ignore[override]  # Type of dict.__hash__ is None.
        """Hash function that depends only on the keys of the Counter, ignoring values."""
        return hash(frozenset(self))

    def __repr__(self) -> str:
        """Print the MHGraph in a compact way."""
        unicode_superscripts: dict[int, str]
        unicode_superscripts = {1: '\u00b9', 2: '\u00b2', 3: '\u00b3', 4: '\u2074',
                                5: '\u2075', 6: '\u2076', 7: '\u2077', 8: '\u2078',
                                9: '\u2079'}

        ordered_hedges: list[HEdge] = sorted(sorted(super().keys()), key=len)  # pylint: disable=no-member

        def superscript(hedge_: HEdge) -> str:
            multiplicity: int = self.get(hedge_, 0)
            return unicode_superscripts.get(multiplicity, f'^{multiplicity}')

        hedge_strings: list[str]
        hedge_strings = [str(h) + superscript(h) for h in ordered_hedges]

        return ','.join(hedge_strings)

    @classmethod
    def fromkeys(  # type: ignore[override]
            cls, _: Iterable[HEdge], __: None | int = ...) -> NoReturn:

        # Mypy needs to be silenced here because `dict` and `counter`
        # have incompatible signatures for `fromkeys`. So no matter
        # how we define this function's signature, it is going to
        # violate one or the other.
        raise NotImplementedError

class GraphNode(at.NodeMixin):
    """This is a MHGraph that can also act as the node in a tree.

    API for interpreting MHGraphs rewriting as trees.

    Each MHGraph starts off as the root of a tree. A rewrite on the graph
    creates a bunch of child-nodes such that the original graph is
    equisatisfiable to the union of the child nodes. Rewriting when applied
    recursively to the nodes will result in a tree of greater height.

    The graph can be written as being equisatisfiable to the leaves of its
    rewrite tree.

    """
    def __init__(self,
                 graph_instance: MHGraph,
                 free: Vertex = vertex(1),
                 parent: None | MHGraph | GraphNode = None,
                 children: None | list[MHGraph] = None):
        "Make MHGraph into a node with relevant args."
        self.graph = graph_instance
        self.parent = parent
        self.free = free
        if children:  # set children only if given
            self.children = list(map(GraphNode, children))

    def __str__(self) -> str:
        """Pretty print a tree."""
        lines: list[str] = []
        for pre, _, node in at.RenderTree(self):
            #pre = ' ' + pre if pre else pre  # add some padding to the front
            line = (f'{pre} {node.graph} '
                    + ("@" + str(node.free) if not node.parent else ""))
            lines.append(line)
        return '\n'.join(lines)

    __repr__ = __str__



# Constructor Functions
# =====================


def hedge(vertex_collection: Collection[int | Vertex] | HEdge) -> HEdge:
    """Constructor-function for HEdge type.

    For definition of HEdge, refer to :ref:`definitionofagraph`.
    This function is idempotent.

    Args:
       vertex_collection (:obj:`Collection[int]`): a nonempty collection (list, tuple,
          set, or frozenset) of Vertices.

    Return:
       Check that each element satisfies the axioms for being a Vertex.
       If yes, then cast to HEdge.

    Raises:
       ValueError: If ``vertex_collection`` is an empty collection.

    """
    if not vertex_collection:
        raise ValueError(f'Encountered empty input {list(vertex_collection)}')
    return HEdge(frozenset(map(vertex, vertex_collection)))


def hgraph(hedge_collection: Collection[Collection[int]] | HGraph) -> HGraph:
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
    return HGraph(set(map(hedge, hedge_collection)))


def mhgraph(edge_collection: Collection[Collection[int | Vertex]]) -> MHGraph:
    """Constructor-function for MHGraph type.

    For definition of a MHGraph, refer to :ref:`definitionofagraph`.
    This function is idempotent.

    Args:
       edge_collection (obj:`Collection[Collection[int]]`): a nonempty Collection
          (counter, list, tuple, set, or frozenset) of nonempty collections of Vertices.

    Return:
       If ``edge_collection`` is a Counter, then this function takes HEdge-multiplicities
       into account (values of the Counter). If each element of the collection satisfies
       the axioms for being an HEdge, then the input is cast as a MHGraph and then a
       MHGraph.

    Raises:
       ValueError: If ``edge_collection`` is an empty collection.

    """
    if not edge_collection:
        raise ValueError(f'Encountered empty input {list(edge_collection)}')

    try:
        # edge_collection is a Counter.

        # Mypy can ignore the fact that elements might not be a
        # defined attribute because we are catcing the AttributeError
        # in the except block.
        return MHGraph(map(hedge, edge_collection.elements()))  # type: ignore[attr-defined]
    except AttributeError:
        # edge_collection is not a Counter.
        return MHGraph(map(hedge, edge_collection))


# Basic Functions
# ===============


def vertices(mhg: HGraph | MHGraph) -> frozenset[Vertex]:
    """Return a `frozenset` of all vertices of a MHGraph."""
    return frozenset.union(*mhg)


def degree(vertex_instance: Vertex, mhg: MHGraph) -> int:
    """Return the degree of a ``vertex_instance`` in a MHGraph.

    This counts multiplicities.
    """
    return sum(multiplicity for hedge, multiplicity in mhg.items()
                if vertex_instance in hedge)


def pick_max_degree_vertex(mhg: MHGraph) -> Vertex:
    """Pick vertex of highest degree."""
    degree_sequence: dict[Vertex, int]
    degree_sequence = {v: degree(v, mhg) for v in vertices(mhg)}
    assert degree_sequence, 'Graph nonempty implies degree sequence nonempty'
    return max(degree_sequence, key=lambda v: degree_sequence[v])


def pick_min_degree_vertex(mhg: MHGraph) -> Vertex:
    """Pick (any one) vertex of lowest degree."""
    vertex_degree_counter: Counter[Vertex]
    vertex_degree_counter = counter(v for hedge in mhg.elements()
                                    for v in hedge)
    # Mypy complains because `min(dict_A, key=dict_B.get)` is
    # mis-typed. However, in the case when `dict_A == dict_B`, it is
    # guaranteed that the `.get` method will not return None. Hence,
    # we silence the mypy error.
    return min(vertex_degree_counter, key=vertex_degree_counter.get)  # type: ignore[arg-type]


def star(mhg: MHGraph, vertex_instance: Vertex) -> tuple[HEdge, ...]:
    """Return the tuple of all HEdges in ``mhg`` incident at ``vertex_instance``."""
    assert vertex_instance in vertices(mhg), f'{vertex_instance} not of vertex_instance of {mhg}'
    return tuple(hedge(h) for h in mhg.elements() if vertex_instance in h)


def link(mhg: MHGraph, vertex_instance: Vertex) -> tuple[HEdge, ...]:
    """Return the link of ``mhg`` at ``vertex_instance``.

    This is the star projected away from ``vertex_instance``.

    """
    return tuple(hedge(set(h) - {vertex_instance}) for h in star(mhg, vertex_instance)
                 if set(h) != {vertex_instance})


def sphr(mhg: MHGraph, vertex_instance: Vertex) -> tuple[HEdge, ...]:
    """Return the list of all HEdges in ``mhg`` *not* incident at ``vertex_instance``."""
    return tuple(hedge(h) for h in mhg.elements() if vertex_instance not in h)


def graph_union(mhg1: Sequence[HEdge] | MHGraph, mhg2: Sequence[HEdge] | MHGraph) -> MHGraph:
    """Union of the two graphs."""
    assert mhg1 or mhg2, f'Encountered empty input {mhg1 = } or {mhg2 = }'
    # Ignore mypy errors because we are checking for attributes before
    # using them.
    if hasattr(mhg1, "__add__"):
        return mhgraph(mhg1 + mhg2)  # type: ignore[operator]
    if hasattr(mhg1, "__or__"):
        return mhgraph(mhg1 | mhg2)  # type: ignore[operator]
    raise TypeError



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


if __name__ == '__main__':  # pragma: no cover
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
    logger.info(degree(Vertex(2), mhgraph([[1, 2], [3, 1, 2], [1, 2]])))
    logger.info('\n')

#!/usr/bin/env python3.8
"""Functions for working with graph-satisfiability and various graph parts."""

# Imports from standard library.
import functools as ft
import itertools as it
from typing import Iterator, List, Optional, Set, Union, cast

# Imports from third-party modules.
from loguru import logger

# Imports from local modules.
import graphsat.cnf as cnf
import graphsat.morphism as morph
import graphsat.prop as prop
import graphsat.sat as sat
from graphsat.mhgraph import (GraphNode, MHGraph, Vertex, degree, graph_union,
                              mhgraph, vertex)
from graphsat.sxpr import AtomicSxpr, SatSxpr


@ft.singledispatch
def satg(arg: Union[bool, MHGraph, SatSxpr]) -> bool:  # type: ignore
    """Sat-solve if it is a graph. Else just return the bool."""
    print(type(arg))
    raise TypeError


@satg.register
def satg_bool(boolean: bool) -> bool:
    """Return the boolean."""
    return boolean


@satg.register
def satg_graph(graph: MHGraph) -> bool:
    """Sat-solve."""
    return sat.mhgraph_pysat_satcheck(graph)


@satg.register
def satg_sxpr(sat_sxpr: SatSxpr) -> bool:  # type: ignore
    """Reduce and then sat-solve."""
    return satg(sat_sxpr.reduce())


def sat_and(graph1: Union[bool, MHGraph, AtomicSxpr],
            graph2: Union[bool, MHGraph, AtomicSxpr]) -> bool:
    """Return the conjunction of the sat-status of each graph."""
    return satg(graph1) and satg(graph2)


def sat_or(graph1: Union[bool, MHGraph, AtomicSxpr],
           graph2: Union[bool, MHGraph, AtomicSxpr]) -> bool:
    """Return the disjunction of the sat-status of each graph."""
    return satg(graph1) or satg(graph2)


def graph_or(graph1: Union[MHGraph, Set[cnf.Cnf]],
             graph2: Union[MHGraph, Set[cnf.Cnf]]) -> Set[cnf.Cnf]:
    """Disjunction of the Cartesian product of Cnfs."""
    if not isinstance(graph1, set):
        graph1 = set(sat.cnfs_from_mhgraph(mhgraph(graph1)))
    if not isinstance(graph2, set):
        graph2 = set(sat.cnfs_from_mhgraph(mhgraph(graph2)))

    product = it.product(graph1, graph2)
    disjunction = it.starmap(prop.cnf_or_cnf, product)
    disjunction_reduced = map(cnf.tautologically_reduce_cnf, disjunction)
    return set(disjunction_reduced)


def graph_and(graph1: Union[MHGraph, Set[cnf.Cnf]],
              graph2: Union[MHGraph, Set[cnf.Cnf]]) -> Union[MHGraph, Set[cnf.Cnf]]:
    """Conjunct the corresponding Cnfs.

    If both arguments are of type MHGraph, then simply compute the
    `graph_union` of the graphs.
    """
    if isinstance(graph1, MHGraph) and isinstance(graph2, MHGraph):
        return graph_union(graph1, graph2)
    if not isinstance(graph1, set):
        graph1 = set(sat.cnfs_from_mhgraph(mhgraph(graph1)))
    if not isinstance(graph2, set):
        graph2 = set(sat.cnfs_from_mhgraph(mhgraph(graph2)))

    product = it.product(graph1, graph2)
    conjunction = it.starmap(prop.cnf_and_cnf, product)
    conjunction_reduced = map(cnf.tautologically_reduce_cnf, conjunction)
    return set(conjunction_reduced)


def graphs_equisat_a_bot(graph1: Set[cnf.Cnf], graph2: Set[cnf.Cnf]) -> bool:
    """Check ∀ x₁ ∈ G₁, ∃ x₂ ∈ G₂, ∀ a ∈ A, x₁[a] ~ ⊥ → x₂[a] ~ ⊥."""
    particular_x1: cnf.Cnf = graph1.pop()
    graph1.add(particular_x1)  # add it back in.

    assignments: list[sat.Assignment]
    assignments = list(sat.generate_assignments(particular_x1))

    def cnf1_falsified(cnf1: cnf.Cnf, assignment: sat.Assignment) -> bool:
        cnf1_assigned: cnf.Cnf = cnf.assign(cnf1, assignment)
        assert all(map(lambda l: isinstance(l, cnf.Bool), cnf.lits(cnf1_assigned)))
        return not sat.cnf_pysat_satcheck(cnf1_assigned)

    def cnf2_falsified(cnf2: cnf.Cnf, assignment: sat.Assignment) -> bool:
        return not sat.cnf_pysat_satcheck(cnf.assign(cnf2, assignment))

    return all(any(all(cnf2_falsified(cnf2, a)
                       for a in assignments if cnf1_falsified(cnf1, a))
                   for cnf2 in graph2) for cnf1 in graph1)


def graph_equisat_mod_sphr(graph1: Union[MHGraph, Set[cnf.Cnf]],
                           graph2: Union[MHGraph, Set[cnf.Cnf]]) -> bool:
    """Check graphs are quisat by the A⊥ criterion.

    This helps us conclude that Sphr∧G₁ is equisat to Sphr∧G₂ by the ⊥
    criterion.
    """
    if not isinstance(graph1, set):
        graph1 = set(sat.cnfs_from_mhgraph(mhgraph(graph1)))
    if not isinstance(graph2, set):
        graph2 = set(sat.cnfs_from_mhgraph(mhgraph(graph2)))

    assert graph1 and graph2
    return graphs_equisat_a_bot(graph1, graph2) \
        and graphs_equisat_a_bot(graph1=graph2, graph2=graph1)


EDGE_SMOOTH = GraphNode(mhgraph([[1, 2], [1, 3]]),
                        free=vertex(1),
                        children=[mhgraph([[2, 3]])])

HEDGE_SMOOTH = GraphNode(mhgraph([[1, 2, 3], [1, 2, 4]]),
                         free=vertex(1),
                         children=[mhgraph([[2, 3, 4]])])

R1 = GraphNode(mhgraph([[1, 2, 3], [1, 2]]),
               free=vertex(1),
               children=[mhgraph([[2, 3]])])

R2 = GraphNode(mhgraph([[1, 2, 3], [1, 2], [1, 3]]),
               free=vertex(1),
               children=[mhgraph([[2]]), mhgraph([[3]])])


R4 = GraphNode(mhgraph([[1, 2, 3], [1, 2, 4], [1, 3, 4]]),
               free=vertex(1),
               children=[mhgraph([[2, 3]]),
                         mhgraph([[2, 4]]),
                         mhgraph([[3, 4]])])

R5 = GraphNode(mhgraph([[1, 2, 3], [1, 4]]),
               free=vertex(1),
               children=[mhgraph([[2, 3, 4]])])

R7 = GraphNode(mhgraph([[1, 2, 3], [1, 2, 3], [1, 2], [1, 3]]),
               free=vertex(1),
               children=[mhgraph([[2, 3]]*3)])


LEAF1 = GraphNode(mhgraph([[1]]),
                  free=vertex(1),
                  children=[])


def pop2(n: int) -> GraphNode:
    """Pop a simple-leaf vertex."""
    assert n > 1
    return GraphNode(mhgraph([[1, 2]]*n),
                     free=vertex(1),
                     children=[mhgraph([[2]]*(n//2))])


def pop3(n: int) -> GraphNode:
    """Pop a hyper-leaf vertex."""
    assert n > 1
    return GraphNode(mhgraph([[1, 2, 3]]*n),
                     free=vertex(1),
                     children=[mhgraph([[2, 3]]*(n//2))])


KNOWN_RULES = [EDGE_SMOOTH, HEDGE_SMOOTH] \
    + [R1, R2, R4, R5, R7] \
    + [pop2(n) for n in range(2, 5)] \
    + [pop3(n) for n in range(2, 9)] \
    + []


def apply_rule(graph: MHGraph, rule: GraphNode) -> List[MHGraph]:
    """Apply the given reduction rule if possible.

    S : MHGraph -> R : list MHGraph
    fv : free Vertex of S

    S <= mhgraph
    - If no, then return mhgraph unchanged.
    - If yes, then store every way in which O is a subgraph of mhgraph.

    Run loop on "m"  m can fit O inside mhgraph.
    mO : MHGraph inside mhgraph
    mfv : Vertex of mO as well as mhgraph
    mReplace : MHGraph

    deg(fv, O) : this number should be preserved.
    Check deg(mfv, mhgraph) == deg(fv, O).
    - If no, then check the next "m".
    - If yes, then do the rewrite.
    mhgraph ->   mhgraph - mO + mReplace
    """
    is_subgraph: bool
    is_subgraph, sub_morphs = morph.subgraph_search(rule.graph,
                                                    graph,
                                                    return_all=True)
    if not is_subgraph:
        return [graph]

    sub_morphs = cast(Iterator[morph.Morphism], sub_morphs)
    for sub_morph in sub_morphs:
        mapped_free: Vertex
        mapped_free = sub_morph.translation[rule.free]
        if degree(mapped_free, graph) != degree(rule.free, rule.graph):
            continue

        mapped_parent: MHGraph
        mapped_parent = morph.graph_image(sub_morph, rule.graph)

        mapped_children: Iterator[MHGraph]
        mapped_children = (morph.graph_image(sub_morph, child.graph)
                           for child in rule.children)

        return [mhgraph(graph - mapped_parent + child) for child in mapped_children]
    return [graph]


@logger.catch
def make_tree(mhgraph: MHGraph, parent: Optional[GraphNode] = None) -> GraphNode:
    """Make a tree starting at mhgraph as root."""
    node = GraphNode(mhgraph, parent=parent or GraphNode(mhgraph))

    for rule in KNOWN_RULES:
        reduction: list[MHGraph] = apply_rule(mhgraph, rule)
        if reduction[0] != mhgraph:
            for child in reduction:
                make_tree(child, parent=node)
            return node
    return node



if __name__ == "__main__":
    from time import time
    with logger.catch(message="Something unexpected happened ..."):
        time0 = time()

#!/usr/bin/env python3.8
"""Functions for working with graph-satisfiability and various graph parts."""

import itertools as it
from typing import Callable, Iterator, List, Set, Union, cast

from loguru import logger
from multipledispatch import dispatch
from typing_extensions import assert_never

from normal_form import cnf, sat, prop
from graphsat import translation
import graphsat.morphism as morph
from graphsat.graph import Vertex, vertex
from graphsat.mhgraph import GraphNode, MHGraph, degree, graph_union, mhgraph
from normal_form.sxpr import AtomicSxpr, SatSxpr


def satg(arg:  bool | MHGraph | SatSxpr[bool | MHGraph]) -> bool:
    """Sat-solve if it is a graph. Else just return the bool."""
    match arg:
        case bool():
            return arg
        case MHGraph():
            return translation.mhgraph_pysat_satcheck(arg)
        case SatSxpr():
            return satg(arg.reduce())
        case _ as unreachable:
            assert_never(unreachable)


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
        graph1 = set(translation.cnfs_from_mhgraph(mhgraph(graph1)))
    if not isinstance(graph2, set):
        graph2 = set(translation.cnfs_from_mhgraph(mhgraph(graph2)))

    product = it.product(graph1, graph2)
    disjunction = it.starmap(prop.cnf_or_cnf, product)
    disjunction_reduced = map(cnf.tauto_reduce, disjunction)
    return set(disjunction_reduced)


@dispatch(MHGraph, MHGraph)
def graph_and(graph1: MHGraph, graph2: MHGraph) -> MHGraph:
    return graph_union(graph1, graph2)

@dispatch(MHGraph, set)  # type: ignore
def graph_and(graph1: MHGraph, set2: set[cnf.Cnf]) -> set[cnf.Cnf]:  # pylint: disable=function-redefined
    set1: set[cnf.Cnf] = set(translation.cnfs_from_mhgraph(mhgraph(graph1)))
    return graph_and(set1, set2)

@dispatch(set, MHGraph)  # type: ignore
def graph_and(set1: set[cnf.Cnf], mhgraph2: MHGraph) -> set[cnf.Cnf]:  # pylint: disable=function-redefined
    return graph_and(mhgraph2, set1)

@dispatch(set, set)  # type: ignore
def graph_and(set1: set[cnf.Cnf], set2: set[cnf.Cnf]) -> set[cnf.Cnf]:  # pylint: disable=function-redefined
    product: it.product[tuple[cnf.Cnf, cnf.Cnf]] = it.product(set1, set2)
    conjunction: it.starmap[cnf.Cnf] = it.starmap(prop.cnf_and_cnf, product)
    conjunction_reduced: map[cnf.Cnf] = map(cnf.tauto_reduce, conjunction)
    return set(conjunction_reduced)

# Override graph_and's type signature.
graph_and: Union[  # type: ignore
    Callable[[MHGraph, MHGraph], MHGraph],
    Callable[[MHGraph | set[cnf.Cnf], MHGraph | set[cnf.Cnf]], set[cnf.Cnf]]]


def graphs_equisat_a_bot(graph1: Set[cnf.Cnf], graph2: Set[cnf.Cnf]) -> bool:
    """Check ∀ x₁ ∈ G₁, ∃ x₂ ∈ G₂, ∀ a ∈ A, x₁[a] ~ ⊥ → x₂[a] ~ ⊥."""
    particular_x1: cnf.Cnf = graph1.pop()
    graph1.add(particular_x1)  # add it back in.

    assignments: list[cnf.Assignment]
    assignments = list(sat.generate_assignments(particular_x1))

    def cnf1_falsified(cnf1: cnf.Cnf, assignment: cnf.Assignment) -> bool:
        cnf1_assigned: cnf.Cnf = cnf.assign(cnf1, assignment)
        assert all(map(lambda l: isinstance(l, cnf.Bool), cnf.lits(cnf1_assigned)))
        return not sat.cnf_pysat_satcheck(cnf1_assigned)

    def cnf2_falsified(cnf2: cnf.Cnf, assignment: cnf.Assignment) -> bool:
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
        graph1 = set(translation.cnfs_from_mhgraph(mhgraph(graph1)))
    if not isinstance(graph2, set):
        graph2 = set(translation.cnfs_from_mhgraph(mhgraph(graph2)))

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

        return [mhgraph(graph - mapped_parent + child) for child in mapped_children]  # type: ignore
    return [graph]


def make_tree(mhgraph_instance: MHGraph, parent: None | GraphNode = None) -> GraphNode:
    """Make a tree starting at mhgraph_instance as root."""
    node = GraphNode(mhgraph_instance, parent=parent or GraphNode(mhgraph_instance))

    for rule in KNOWN_RULES:
        reduction: list[MHGraph] = apply_rule(mhgraph_instance, rule)
        if reduction[0] != mhgraph_instance:
            for child in reduction:
                make_tree(child, parent=node)
            return node
    return node



if __name__ == "__main__":  # pragma: no cover
    from time import time
    with logger.catch(message="Something unexpected happened ..."):
        time0 = time()

#! /usr/bin/env python3.8

from collections import Counter as counter

import pytest
from hypothesis import Verbosity, assume, given, settings
from hypothesis import strategies as st

from graphsat.graph import Graph, Vertex, vertex
from graphsat.mhgraph import (GraphNode, HEdge, HGraph, MHGraph, degree,
                              graph_from_mhgraph, graph_union, hedge, hgraph,
                              mhgraph, mhgraph_from_graph, vertices)


def test__repr() -> None:
    assert repr(mhgraph([[1, 2], [2, 3], [3, 2]])) in \
    ['(1, 2)¹,(2, 3)²', '(1, 2)¹,(3, 2)²', '(2, 1)¹,(2, 3)²', '(2, 1)¹,(3, 2)²']


@given(st.lists(st.integers(min_value=1), min_size=1))
def test_hedge_on_list_of_integers_input(instance: list[int]) -> None:
    pytest.raises(ValueError, hedge, [])
    pytest.raises(ValueError, hedge, [0])
    assert hedge(instance) == frozenset(instance)


st.register_type_strategy(HEdge, st.frozensets(st.from_type(Vertex),
                                               min_size=1, max_size=5).map(hedge))

@given(st.from_type(HEdge))
def test_hedge_on_hedge_input(instance: HEdge) -> None:
    assert hedge(instance) == frozenset(instance)


@given(st.lists(st.from_type(HEdge), min_size=1))
def test_hgraph_on_list_of_hedge_input(instance: list[HEdge]) -> None:
    pytest.raises(ValueError, hgraph, [])
    assert hgraph(instance) == frozenset(instance)
    assert hgraph(hgraph(instance)) == hgraph(instance)


st.register_type_strategy(HGraph, st.frozensets(st.from_type(HEdge),
                                                min_size=1, max_size=10).map(hgraph))


@given(st.from_type(HGraph))
def test_hgraph_on_hgraph_input(instance: HGraph) -> None:
    assert hgraph(instance) == frozenset(instance)
    assert hgraph(hgraph(instance)) == hgraph(instance)


@given(st.lists(st.from_type(HEdge), min_size=1))
def test_mhgraph_on_list_of_hedge_input(instance: list[HEdge]) -> None:
    pytest.raises(ValueError, mhgraph, [])
    assert mhgraph(instance) == counter(instance)
    assert mhgraph(mhgraph(instance)) == mhgraph(counter(instance))
    assert hash(mhgraph(instance))


st.register_type_strategy(MHGraph, st.dictionaries(st.from_type(HEdge),
                                                   st.integers(min_value=0, max_value=10),
                                                   min_size=1, max_size=20).map(mhgraph))

@given(st.from_type(MHGraph))
def test_mhgraph_on_mhgraph_input(instance: MHGraph) -> None:
    # Test if instance is hashable.
    {instance: 1}
    assert mhgraph(instance) == counter(instance)
    assert mhgraph(mhgraph(instance)) == mhgraph(counter(instance))


@given(st.one_of(st.from_type(HGraph), st.from_type(MHGraph)))
def test_vertices(instance: HGraph | MHGraph) -> None:
    assert vertices(instance) == {vertex_instance for edge_instance in instance
                                     for vertex_instance in edge_instance}

@pytest.mark.parametrize("vertex_instance,degree_output",
                         [(2, 3),
                          (1, 2),
                          (4, 1),
                          (5, 0)])
def test_degree(vertex_instance: int, degree_output: int) -> None:
    assert degree(vertex(vertex_instance), mhgraph([[1, 2], [3, 4, 2], [1, 2]])) == degree_output


@given(st.from_type(MHGraph), st.from_type(MHGraph))
def test_graph_union(instance1: MHGraph, instance2: MHGraph) -> None:
    assert graph_union(instance1, instance2) == mhgraph(instance1 + instance2)  # type: ignore


@given(st.from_type(MHGraph), st.from_type(Graph))
@settings(verbosity=Verbosity.verbose, max_examples=20)
def test_graph_from_mhgraph(mhgraph_instance: MHGraph, graph_instance: Graph) -> None:
    # `graph_from_mhgraph ∘ mhgraph = id` on type Graph.
    assert graph_from_mhgraph(mhgraph(graph_instance)) == graph_instance
    # MHGraphs of restricted edge sizes can be converted to Graphs.
    assume(all(len(hedge) <= 2 for hedge in mhgraph_instance))
    assert isinstance(graph_from_mhgraph(mhgraph_instance), Graph)


@given(st.from_type(Graph))
def test_mhgraph_from_graph(graph_instance: Graph) -> None:
    assert isinstance(mhgraph_from_graph(graph_instance), MHGraph)


@given(st.from_type(MHGraph), st.from_type(Vertex))
def test_graphnode(mhgraph_instance: MHGraph, vertex_instance: Vertex) -> None:
    gn: GraphNode = GraphNode(graph_instance=mhgraph_instance,
                              free=vertex_instance)
    assert str(gn)

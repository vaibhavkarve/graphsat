#! /usr/bin/env python3.10

from typing import Collection

import pytest
from hypothesis import given
from hypothesis import strategies as st

from graphsat.graph import Edge, Graph, Vertex, edge, graph, vertex, vertices


@given(st.integers(min_value=1))
def test_vertex_on_integer_input(instance: int) -> None:
    assert vertex(instance) == instance
    assert vertex(vertex(instance)) == vertex(instance)


st.register_type_strategy(Vertex, st.integers(min_value=1, max_value=100).map(vertex))


@given(st.from_type(Vertex))
def test_vertex_on_vertex_input(instance: int) -> None:
    assert vertex(instance) == instance
    assert vertex(vertex(instance)) == vertex(instance)


@given(st.lists(st.integers(min_value=1), min_size=1, max_size=2))
def test_edge_on_integer_collection_input(instance: Collection[int]) -> None:
    pytest.raises(ValueError, edge, [])
    pytest.raises(ValueError, edge, [1, 2, 3])
    assert edge(instance) == frozenset(map(vertex, instance))
    assert edge(edge(instance)) == edge(instance)


st.register_type_strategy(
    Edge,
    st.frozensets(st.from_type(Vertex), min_size=1, max_size=2).map(edge))


@given(st.from_type(Edge))
def test_edge_on_edge_input(instance: Edge) -> None:
    assert edge(instance) == frozenset(map(vertex, instance))
    assert edge(edge(instance)) == edge(instance)


@given(st.lists(st.lists(st.integers(min_value=1), min_size=1, max_size=2), min_size=1))
def test_graph_on_collection_of_collection_of_integers_input(
        instance: Collection[Collection[int]]) -> None:
    pytest.raises(ValueError, graph, [])
    assert graph(instance) == set(map(frozenset, instance))  # type: ignore  # Mypy is not able to infer that frozenset is a Callable.
    # Test for idempotence.
    assert graph(graph(instance)) == graph(instance)


st.register_type_strategy(
    Graph,
    st.frozensets(st.from_type(Edge), min_size=1, max_size=10).map(graph))


@given(st.from_type(Graph))
def test_graph_on_graph_input(instance: Graph) -> None:
    assert graph(instance) == set(map(frozenset, instance))  # type: ignore  # Mypy is not able to infer that frozenset is a Callable.
    # Test for idempotence.
    assert graph(graph(instance)) == graph(instance)


def test_graph_repr() -> None:
    assert repr(graph([[1, 2], [2, 3], [3, 2]])) == '(1,2),(2,3)'


@given(st.from_type(Graph))
def test_vertices(instance: Graph) -> None:
    assert vertices(instance) == {vertex_instance for edge_instance in instance
                                  for vertex_instance in edge_instance}

#!/usr/bin/env python3.10
from typing import Collection

import attr
import pytest
from hypothesis import assume, given
from hypothesis import strategies as st

from graphsat.cnf import (Assignment, Bool, Clause, Cnf, Lit, Variable,
                          absolute_value, assign, assign_variable_in_clause,
                          assign_variable_in_cnf, assign_variable_in_lit,
                          clause, cnf, int_repr, lit, lits, neg,
                          tautologically_reduce_clause,
                          tautologically_reduce_cnf, variable)


@given(st.integers())
def test_variable(instance: int) -> None:
    # Check that ValueError is raised on invalid input.
    assert pytest.raises(ValueError, variable, 0)
    assert pytest.raises(ValueError, variable, -1)

    # Assume that input is valid.
    assume(instance > 0)

    # Check for equality comparison between Variable and the underlying int.
    assert variable(instance) == instance
    # Check for idempotence.
    assert variable(variable(instance)) == instance


st.register_type_strategy(Variable, st.integers(min_value=1).map(variable))


@given(st.sampled_from(Bool))
def test_Bool(instance: Bool) -> None:
    assert instance in Bool
    assert instance == instance  # Check for consistency, and __eq__.
    assert instance not in (0, 1)  # Bool is not a subtype of int.
    assert instance not in (True, False)  # Bool != bool
    assert instance not in ("T", "F")  # Bool is not a subtype of str.
    assert instance in (Bool.TRUE, Bool.FALSE)  # Bool comparison with itself.
    assert hasattr(instance, "__hash__")  # Bool is hashable.
    assert instance < 1  # every Bool member is less than every int.
    assert Bool.FALSE < Bool.TRUE
    with pytest.raises(TypeError):
        assert instance < "T"


@given(st.from_type(Bool | int), st.from_type(Bool | int))
def test_lit_class(instance: Bool | int, other: Bool | int) -> None:
    assert Lit(instance) == Lit(instance)  # Self-equality.
    assert not Lit(instance) < Lit(instance)  # Order is defined.
    if isinstance(instance, int) and isinstance(other, int):
        assert (instance < other) == (Lit(instance) < Lit(other))  # Lits are ordered by value.
    assert str(Lit(instance))
    # Check that Lits are frozen once created.
    with pytest.raises(attr.exceptions.FrozenInstanceError):
        lit1: Lit = Lit(value=3)
        lit1.value += 1  # type: ignore  # Silence mypy for the sake of testing that Lit.value is frozen.


@given(st.from_type(Bool | int))  #  type: ignore  # Mypy errors on union type.
def test_lit_on_int_and_bool_input(instance: Bool | int) -> None:
    pytest.raises(ValueError, lit, 0)
    pytest.raises(TypeError, lit, "T")
    assume(instance)
    assert lit(instance) == Lit(value=instance)
    assert lit(lit(instance)) == lit(instance)  # Check for idempotence.


st.register_type_strategy(Lit,
                          st.one_of(st.integers().filter(lambda x: x),
                                    st.sampled_from(Bool))
                          .map(lit))


@given(st.from_type(Lit))
def test_lit_on_lit_input(instance: Lit) -> None:
    assert lit(instance) == instance  # Check that lit does not modify Lit instances.
    assert lit(instance) is instance
    assert lit(lit(instance)) == lit(instance)  # Check for idempotence.


@given(st.lists(st.from_type(Bool | int | Lit),  # type: ignore  # Mypy errors on union type.
                min_size=1))
def test_clause(instance: list[Bool | int | Lit]) -> None:
    pytest.raises(ValueError, clause, [])
    # Invalid input: zero value in collection.
    assume(all(instance))

    assert clause(instance) == set(map(lit, instance))  # Check type and value of output.
    assert clause(clause(instance)) == clause(instance)  # Check for idempotence.


st.register_type_strategy(Clause,
                          st.frozensets(st.from_type(Lit), min_size=1)
                          .map(clause))


@given(st.from_type(Clause))
def test_clause_on_clause_input(instance: Clause) -> None:
    assert clause(instance) == set(map(lit, instance))  # Check type and value of output.
    assert clause(clause(instance)) == clause(instance)  # Check for idempotence.


@given(st.lists(st.lists(st.from_type(Bool | int | Lit),  #  type: ignore  # Mypy errors on union type.
                         min_size=1), min_size=1))
def test_cnf_on_collection_input(instance: Collection[Collection[Bool | int | Lit]]) -> None:
    # Invalid input: empty collection.
    assume(instance)
    # Invalid input: at least one of the sub-collections is empty.
    assume(all(instance))
    # Invalid input: at least element in at least one sub-collection is zero.
    assume(all(map(all, instance)))

    # Check type and value of output.
    assert cnf(instance) == set(map(clause, instance))
    # Check for idempotence.
    assert cnf(cnf(instance)) == cnf(instance)


st.register_type_strategy(Cnf,
                          st.frozensets(st.from_type(Clause), min_size=1)
                          .map(cnf))


@given(st.from_type(Cnf))
def test_cnf_on_cnf_input(instance: Cnf) -> None:
    # Check type and value of output.
    assert cnf(instance) == set(map(clause, instance))
    # Check for idempotence.
    assert cnf(cnf(instance)) == cnf(instance)


def test_cnf_string_on_example() -> None:
    assert str(cnf([[1, -2], [3, Bool.TRUE]])) in ("Cnf({Clause({Bool.TRUE, 3}), Clause({-2, 1})})",
                                                   "Cnf({Clause({-2, 1}), Clause({Bool.TRUE, 3})})")


@given(st.from_type(Lit))
def test_neg(instance: Lit) -> None:
    pytest.raises(TypeError, neg, Bool.TRUE)
    # Check for involution.
    assert neg(instance) != instance
    assert neg(neg(instance)) == instance

    # Check result on Bool-valued literals.
    assert neg(lit(Bool.TRUE)) == lit(Bool.FALSE)
    assert neg(lit(Bool.FALSE)) == lit(Bool.TRUE)

    # Check result on int-valued literals.
    if isinstance(instance.value, int):
        assert neg(instance) == lit(-instance.value)


@given(st.from_type(Lit))
def test_absolute_value(instance: Lit) -> None:
    # Check for idempotence.
    assert absolute_value(absolute_value(instance)) == absolute_value(instance)

    # Check return value.
    assert absolute_value(lit(Bool.TRUE)) == lit(Bool.TRUE)
    assert absolute_value(lit(Bool.FALSE)) == lit(Bool.TRUE)
    if isinstance(instance.value, int):
        absolute_value(instance) == lit(abs(instance.value))


@given(st.from_type(Cnf))
def test_lits(instance: Cnf) -> None:
    assert lits(instance) == {lit_collection for clause_collection in instance
                              for lit_collection in clause_collection}


@given(st.from_type(Clause))
def test_tautologically_reduce_clause(instance: Clause) -> None:
    # Check for idempotence.
    assert tautologically_reduce_clause(tautologically_reduce_clause(instance)) \
       == tautologically_reduce_clause(instance)


@pytest.mark.parametrize(
    "lit_collection,output",
    [
        ({1, Bool.TRUE}, [Bool.TRUE]),
        ({Bool.FALSE}, [Bool.FALSE]),
        ({1, Bool.FALSE}, [1]),
        ({1, -1}, [Bool.TRUE]),
    ])
def test_tautologically_reduce_clause_with_examples(
        lit_collection: Collection[Bool | int],
        output: Collection[Bool | int]) -> None:
    assert tautologically_reduce_clause(clause(lit_collection)) == clause(output)


@given(st.from_type(Cnf))
def test_tautologically_reduce_cnf(instance: Cnf) -> None:
    # Check for idempotence.
    assert tautologically_reduce_cnf(tautologically_reduce_cnf(instance)) \
       == tautologically_reduce_cnf(instance)


@pytest.mark.parametrize(
    "clause_collection,output",
    [
        # Cases where Clause reductions appear within Cnf reductions.
        ([[1, Bool.TRUE], [1, 2]], [[1, 2]]),
        ([[Bool.FALSE], [1, 2]], [[Bool.FALSE]]),
        ([[1, Bool.FALSE], [1, 2]], [[1], [1, 2]]),
        ([[1, -1], [1, 2]], [[1, 2]]),

        # Cases where we might have two simultaneous clause reductions
        ([[1, Bool.TRUE], [Bool.FALSE]], [[Bool.FALSE]]),
        ([[1, Bool.TRUE], [1, Bool.FALSE]], [[1]]),
        ([[1, Bool.TRUE], [1, -1]], [[Bool.TRUE]]),
        ([[Bool.FALSE], [1, Bool.FALSE]], [[Bool.FALSE]]),
        ([[Bool.FALSE], [1, -1]], [[Bool.FALSE]]),
        ([[1, Bool.FALSE], [1, -1]], [[1]]),

        # Cases where we might have a cnf-related tautology
        ([[1], [Bool.FALSE]], [[Bool.FALSE]]),
        ([[Bool.TRUE]], [[Bool.TRUE]]),
        ([[1], [Bool.TRUE]], [[1]]),
    ])
def test_tautologically_reduce_cnf_with_examples(
        clause_collection: Collection[Collection[Bool | int]],
        output: Collection[Collection[Bool | int]]) -> None:
    assert tautologically_reduce_cnf(cnf(clause_collection)) == cnf(output)


@given(st.integers(min_value=1), st.from_type(Bool))
def test_assign_variable_in_lit(positive_int: int, boolean: Bool) -> None:
    assert assign_variable_in_lit(
        lit(positive_int), variable(positive_int), boolean) == lit(boolean)
    assert assign_variable_in_lit(
        lit(- positive_int), variable(positive_int), boolean) == neg(lit(boolean))
    assert assign_variable_in_lit(
        lit(positive_int + 1), variable(positive_int), boolean) == lit(positive_int + 1)


@given(st.from_type(Lit), st.from_type(Variable), st.from_type(Bool))
def test_assign_variable_in_lit_idempotence(
        literal: Lit, variable_instance: Variable, boolean: Bool) -> None:
    assign_once: Lit = assign_variable_in_lit(literal, variable_instance, boolean)
    assert assign_variable_in_lit(assign_once, variable_instance, boolean) == assign_once


@pytest.mark.parametrize(
    "lit_collection,positive_integer,boolean,output",
    [
        ([1, -2], 1, Bool.TRUE, {Bool.TRUE}),
        ([1, -2], 1, Bool.FALSE, {-2}),
        ([1, -2, -1], 1, Bool.TRUE, {Bool.TRUE}),
        ([1, -2, -1], 1, Bool.FALSE, {Bool.TRUE}),
        ([1, -2], 2, Bool.TRUE, {1}),
        ([1, -2], 2, Bool.FALSE, {Bool.TRUE}),
        ([1, -2, -1], 2, Bool.TRUE, {Bool.TRUE}),
        ([1, -2, -1], 2, Bool.FALSE, {Bool.TRUE}),
    ])
def test_assign_variable_in_clause_with_example_cases(
        lit_collection: Collection[Bool | int],
        positive_integer: int,
        boolean: Bool,
        output: set[Bool]) -> None:
    assign_variable_in_clause(clause(lit_collection), variable(positive_integer), boolean) == output


@given(st.from_type(Clause), st.from_type(Variable), st.from_type(Bool))
def test_assign_variable_in_clause(
        clause_instance: Clause, variable_instance: Variable, boolean: Bool) -> None:
    assign_once: Clause = assign_variable_in_clause(clause_instance, variable_instance, boolean)
    assert assign_variable_in_clause(assign_once, variable_instance, boolean) == assign_once


@pytest.mark.parametrize(
    "clause_collection,positive_int,boolean,output",
    [
        ([[1, -2], [-1, 3]], 1, Bool.TRUE, [[3]]),
        ([[1, -2], [-1, 3]], 1, Bool.FALSE, [[-2]]),
    ])
def test_assign_variable_in_cnf(
        clause_collection: Collection[Collection[Bool | int]],
        positive_int: int,
        boolean: Bool,
        output: Collection[Collection[Bool | int]],
) -> None:
    assert assign_variable_in_cnf(
        cnf(clause_collection), variable(positive_int), boolean) == cnf(output)

@given(st.from_type(Cnf), st.from_type(Variable), st.from_type(Bool))
def test_assign_variable_in_cnf_idempotence(
        cnf_instance: Cnf,
        variable_instance: Variable,
        boolean: Bool) -> None:
    assign_once: Cnf = assign_variable_in_cnf(cnf_instance, variable_instance, boolean)
    assert assign_variable_in_cnf(assign_once, variable_instance, boolean) == assign_once


@given(st.from_type(Cnf), st.dictionaries(st.from_type(Variable),
                                          st.from_type(Bool)))
def test_assign(cnf_instance: Cnf, assignment: Assignment) -> None:
    assign_once: Cnf = assign(cnf_instance, assignment)
    assert assign(assign_once, assignment) == assign_once
    assert assign(cnf_instance, {}) == tautologically_reduce_cnf(cnf_instance)


@pytest.mark.parametrize(
    "clause_collection,assignment_dict,output",
    [
        ([[1, -2], [-1, 3]], {1: Bool.TRUE}, [[3]]),
        ([[1, -2], [-1, 3]], {1: Bool.TRUE, 2: Bool.FALSE}, [[3]]),
        ([[1, -2], [-1, 3]], {1: Bool.TRUE, 2: Bool.FALSE, 3: Bool.FALSE}, [[Bool.FALSE]]),
        ([[Bool.TRUE]], {1: Bool.TRUE}, [[Bool.TRUE]]),
        ([[Bool.TRUE]], {}, [[Bool.TRUE]]),
        ([[Bool.FALSE]], {}, [[Bool.FALSE]]),
        ([[1]], {}, [[1]]),
    ])
def test_assign_with_examples(
        clause_collection: Collection[Collection[Bool | int]],
        assignment_dict: dict[int, Bool],
        output: Collection[Collection[Bool | int]]) -> None:
    assert assign(cnf(clause_collection),
                  {variable(k): v for k, v in assignment_dict.items()}) == cnf(output)


def test_int_repr() -> None:
    assert int_repr(cnf([[1], [Bool.TRUE]])) in [((Bool.TRUE, ), (1, )),
                                                 ((1, ), (Bool.TRUE, ))]

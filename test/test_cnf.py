#!/usr/bin/env python3

import pytest
from cnf import *

def test_Bool():
    assert TRUE == TRUE
    assert TRUE not in [1, 2, 3]
    assert TRUE in [1, 2, 3, TRUE]
    assert isinstance(TRUE, Bool)
    assert not isinstance(TRUE, bool)


def test_variable():
    assert variable(1) == 1
    assert variable(11) == 11
    assert variable(variable(2)) == variable(2)  # Test for idempotence
    with pytest.raises(ValueError):
        variable(0)


def test_literal():
    assert literal(1) == 1
    assert literal(-1) == -1
    assert literal(11) ==  11
    assert literal(TRUE) == TRUE
    assert literal(FALSE) == FALSE
    assert literal(literal(2)) == literal(2)  # Test for idempotence.
    assert literal(literal(TRUE)) == literal(TRUE)  # Test for idempotence.
    assert literal(literal(FALSE)) == literal(FALSE)  # Test for idempotence.

    with pytest.raises(ValueError):
        literal(0)


def test_clause():
    assert clause([1, 2, -3]) == {1, 2, -3}
    assert clause([1, 2]) == {1, 2}
    assert clause([1, -1, 2]) == {1, -1, 2}
    assert clause([TRUE]) == {TRUE}
    assert clause([FALSE]) == {FALSE}
    assert clause([1, TRUE]) == {1, TRUE}
    assert clause([1, FALSE]) == {1, FALSE}
    assert clause([1, TRUE, FALSE]) == {1, TRUE, FALSE}
    assert clause([1]) == {1}

    # Tests for idempotence
    assert clause(clause([1, 2, -3])) == clause([1, 2, -3])
    assert clause(clause([TRUE])) == clause([TRUE])
    assert clause(clause([FALSE])) == clause([FALSE])

    with pytest.raises(ValueError):
        clause([])


def test_cnf():
    assert cnf([[1, 2, -3], [-4, 5]]) == {frozenset([1, 2, -3]), frozenset([-4, 5])}
    assert cnf([[1, 1, -1], [1, -1]]) == {frozenset([1, -1])}
    assert cnf([[1, 2, TRUE], [3, FALSE]]) == {frozenset([1, 2, TRUE]),
                                               frozenset([3, FALSE])}
    assert cnf([[1, 2, 3], [4, 5], [TRUE]]) == {frozenset([1, 2, 3]),
                                                frozenset([4, 5]),
                                                frozenset([TRUE])}
    assert cnf([[TRUE], [TRUE, TRUE]]) == {frozenset([TRUE])}
    assert cnf([[1]]) == {frozenset([1])}
    assert cnf([[-1]]) == {frozenset([-1])}

    # Test for idempotence.
    assert cnf(cnf([[1, 2, 3], [-4, 5]])) == cnf([[1, 2, 3], [-4, 5]])

    with pytest.raises(ValueError):
        cnf([])


def test_neg():
    assert neg(1) == -1
    assert neg(-1) == 1
    assert neg(23) == -23

    # Test for involution.
    assert neg(neg(1)) == 1
    assert neg(neg(-1)) == -1

    with pytest.raises(ValueError):
        neg(0)
    with pytest.raises(ValueError):
        neg(TRUE)
    with pytest.raises(ValueError):
        neg(FALSE)


def test_absolute_value():
    assert absolute_value(1) == 1
    assert absolute_value(-1) == 1

    # Test for idempotence.
    assert absolute_value(absolute_value(1)) == absolute_value(1)
    assert absolute_value(absolute_value(-1)) == absolute_value(-1)

    with pytest.raises(ValueError):
        absolute_value(TRUE)
    with pytest.raises(ValueError):
        absolute_value(FALSE)
    with pytest.raises(ValueError):
        absolute_value(0)


def test_literals():
    assert literals(cnf([[1, -2],[3, TRUE], [FALSE]])) == {1, -2, 3, TRUE, FALSE}


def test_tautologically_reduce_clause():
    with pytest.raises(ValueError):
        tautologically_reduce_clause(set())  # empty input raises an error.
    assert tautologically_reduce_clause(clause([1, TRUE])) == clause([TRUE])
    assert tautologically_reduce_clause(clause([FALSE])) == clause([FALSE])
    assert tautologically_reduce_clause(clause([1, FALSE])) == clause([1])
    assert tautologically_reduce_clause(clause([1, -1])) == clause([TRUE])

    # Test for idempotence
    assert tautologically_reduce_clause(tautologically_reduce_clause(clause([1, -2, 3, 3]))) \
        == tautologically_reduce_clause(clause([1, -2, 3, 3]))


def test_tautologically_reduce_cnf():
    with pytest.raises(ValueError):
        tautologically_reduce_cnf(set(frozenset()))  # empty input raises an error.

    # clause reductions should work within cnf reductions
    assert tautologically_reduce_cnf(cnf([[1, TRUE], [1, 2]])) == cnf([[1, 2]])
    assert tautologically_reduce_cnf(cnf([[FALSE], [1, 2]])) == cnf([[FALSE]])
    assert tautologically_reduce_cnf(cnf([[1, FALSE], [1, 2]])) == cnf([[1], [1, 2]])
    assert tautologically_reduce_cnf(cnf([[1, -1], [1, 2]])) == cnf([[1, 2]])

    # cases where we might have two simultaneous clause reductions
    assert tautologically_reduce_cnf(cnf([[1, TRUE], [FALSE]])) == cnf([[FALSE]])
    assert tautologically_reduce_cnf(cnf([[1, TRUE], [1, FALSE]])) == cnf([[1]])
    assert tautologically_reduce_cnf(cnf([[1, TRUE], [1, -1]])) == cnf([[TRUE]])
    assert tautologically_reduce_cnf(cnf([[FALSE], [1, FALSE]])) == cnf([[FALSE]])
    assert tautologically_reduce_cnf(cnf([[FALSE], [1, -1]])) == cnf([[FALSE]])
    assert tautologically_reduce_cnf(cnf([[1, FALSE], [1, -1]])) == cnf([[1]])

    # cases where we might have a cnf-related tautology
    assert tautologically_reduce_cnf(cnf([[1], [FALSE]])) == cnf([[FALSE]])
    assert tautologically_reduce_cnf(cnf([[TRUE]])) == cnf([[TRUE]])
    assert tautologically_reduce_cnf(cnf([[1], [TRUE]])) == cnf([[1]])

    # Test for idempotence.
    assert tautologically_reduce_cnf(tautologically_reduce_cnf(cnf([[1, 2], [-2]]))) \
        == tautologically_reduce_cnf(cnf([[1, 2], [-2]]))



def test_assign_variable_in_literal():
    assert assign_variable_in_literal(1, 1, TRUE) == TRUE
    assert assign_variable_in_literal(1, 1, FALSE) == FALSE
    assert assign_variable_in_literal(-1, 1, TRUE) == FALSE
    assert assign_variable_in_literal(-1, 1, FALSE) == TRUE
    assert assign_variable_in_literal(1, 2, TRUE) == 1
    assert assign_variable_in_literal(TRUE, 1, TRUE) == TRUE
    assert assign_variable_in_literal(FALSE, 1, TRUE) == FALSE

    # Test for idempotence
    assert assign_variable_in_literal(assign_variable_in_literal(1, 1, TRUE), 1, TRUE) \
        == assign_variable_in_literal(1, 1, TRUE)
    assert assign_variable_in_literal(assign_variable_in_literal(-1, 1, TRUE), 1, TRUE) \
        == assign_variable_in_literal(-1, 1, TRUE)


def test_assign_variable_in_clause():
    assert assign_variable_in_clause(clause([1, -2]), 1, TRUE) == {TRUE}
    assert assign_variable_in_clause(clause([1, -2]), 1, FALSE) == {-2}
    assert assign_variable_in_clause(clause([1, -2, -1]), 1, TRUE) == {TRUE}
    assert assign_variable_in_clause(clause([1, -2, -1]), 1, FALSE) == {TRUE}
    assert assign_variable_in_clause(clause([1, -2]), 2, TRUE) == {1}
    assert assign_variable_in_clause(clause([1, -2]), 2, FALSE) == {TRUE}
    assert assign_variable_in_clause(clause([1, -2, -1]), 2, TRUE) == {TRUE}
    assert assign_variable_in_clause(clause([1, -2, -1]), 2, FALSE) == {TRUE}
    with pytest.raises(ValueError):
        assign_variable_in_clause([], 1, TRUE)

    # Test for idempotence
    assert assign_variable_in_clause(assign_variable_in_clause(clause([1, -2, -1]),
                                                               2, FALSE), 2, FALSE) \
        == assign_variable_in_clause(clause([1, -2, -1]), 2, FALSE)


def test_assign_variable_in_cnf():
    assert assign_variable_in_cnf(cnf([[1, -2], [-1, 3]]), 1, TRUE) == cnf([[3]])
    assert assign_variable_in_cnf(cnf([[1, -2], [-1, 3]]), 1, FALSE) == cnf([[-2]])

    # Test for idempotence.
    assert assign_variable_in_cnf(assign_variable_in_cnf(cnf([[1, -2], [-1, 3]]),
                                                         1, FALSE), 1, FALSE) \
        == assign_variable_in_cnf(cnf([[1, -2], [-1, 3]]), 1, FALSE)

    with pytest.raises(ValueError):
        assign_variable_in_cnf([[]], 1, TRUE)


def test_assign():
    assert assign(cnf([[1, -2], [-1, 3]]), {1: TRUE}) == cnf([[3]])
    assert assign(cnf([[1, -2], [-1, 3]]), {1: TRUE, 2: FALSE}) == cnf([[3]])
    assert assign(cnf([[1, -2], [-1, 3]]), {1: TRUE, 2: FALSE, 3: FALSE}) == cnf([[FALSE]])
    assert assign(cnf([[TRUE]]), {1: TRUE}) == cnf([[TRUE]])
    assert assign(cnf([[TRUE]]), {}) == cnf([[TRUE]])
    assert assign(cnf([[FALSE]]), {}) == cnf([[FALSE]])
    assert assign(cnf([[1]]), {}) == cnf([[1]])

    # Test for idempotence.
    assert assign(assign(cnf([[1, -2], [-1, 3]]), {1: TRUE}), {1: TRUE}) \
        == assign(cnf([[1, -2], [-1, 3]]), {1: TRUE})

    with pytest.raises(ValueError):
        assign([[]], {1: TRUE})


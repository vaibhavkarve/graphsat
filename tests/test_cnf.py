#!/usr/bin/env python3.8
import pytest
from graphsat.cnf import *


def test_variable():
    assert variable(1) == 1
    assert variable(11) == 11
    assert variable(variable(2)) == variable(2)  # Test for idempotence
    pytest.raises(ValueError, variable, 0)


def test_Bool():
    assert TRUE == TRUE  # check for consistency
    assert TRUE not in [1, 2, 3]  # check that eq is working
    assert TRUE in {1, 2, 3, TRUE}  # check that eq and hash are working
    assert isinstance(TRUE, Bool)  # check that python recognizes the class correctly
    assert not isinstance(TRUE, bool)  # check that Bool and bool are district


def test_lit():
    assert lit(1) == 1
    assert lit(-1) == -1
    assert lit(11) == 11
    assert lit(TRUE) == TRUE
    assert lit(FALSE) == FALSE
    assert lit(lit(2)) == lit(2)  # Test for idempotence.
    assert lit(lit(TRUE)) == lit(TRUE)  # Test for idempotence.
    assert lit(lit(FALSE)) == lit(FALSE)  # Test for idempotence.

    pytest.raises(ValueError, lit, 0)


def test_clause():
    assert clause([1, 2, -3]) == {1, 2, -3}  # check for correct type
    assert clause([1, -1, 2]) == {1, -1, 2}  # +ve and -ve Lits are treated as distinct
    assert clause([TRUE]) == {TRUE}  # TRUE can be part of a Clause
    assert clause([FALSE]) == {FALSE}  # FALSE can be part of a Clause
    assert clause([1, TRUE]) == {1, TRUE}  # TRUE is distinct from 1 in a Clause
    assert clause([-1, FALSE]) == {-1, FALSE}  # FALSE is distinct from -1 in a Clause
    assert clause([1, TRUE, FALSE]) == {
        1,
        TRUE,
        FALSE,
    }  # TRUE and FALSE can both appear

    # Tests for idempotence
    assert clause(clause([1, 2, -3])) == clause([1, 2, -3])
    assert clause(clause([TRUE])) == clause([TRUE])
    assert clause(clause([FALSE])) == clause([FALSE])

    pytest.raises(ValueError, clause, [])


def test_cnf():
    fs = frozenset  # a temporary alias for frozenset

    # Generic example use-case
    assert cnf([[1, 2, -3], [-4, 5]]) == {fs([1, 2, -3]), fs([-4, 5])}

    # Test for removing repetitions
    assert cnf([[1, 1, -1], [1, -1]]) == {fs([1, -1])}

    # Cnf with TRUE and FALSE inside a Clause
    assert cnf([[1, 2, TRUE], [3, FALSE]]) == {fs([1, 2, TRUE]), fs([3, FALSE])}

    # Cnf with a Bool-only Clause
    assert cnf([[1, 2, 3], [FALSE], [TRUE]]) == {fs([1, 2, 3]), fs([FALSE]), fs([TRUE])}
    assert cnf([[TRUE], [TRUE, TRUE]]) == {fs([TRUE])}

    # Single-Lit-single-Clause Cnf
    assert cnf([[1]]) == {fs([1])}
    assert cnf([[-1]]) == {fs([-1])}

    # Test for idempotence.
    assert cnf(cnf([[1, 2, 3], [-4, 5]])) == cnf([[1, 2, 3], [-4, 5]])

    pytest.raises(ValueError, cnf, [])
    pytest.raises(ValueError, cnf, [[]])


def test_neg():
    assert neg(lit(1)) == lit(-1)
    assert neg(lit(-1)) == lit(1)
    assert neg(lit(23)) == lit(-23)
    assert neg(TRUE) == FALSE
    assert neg(FALSE) == TRUE

    # Test for involution.
    assert neg(neg(lit(1))) == lit(1)
    assert neg(neg(lit(-1))) == lit(-1)

    pytest.raises(ValueError, neg, 0)


def test_absolute_value():
    assert absolute_value(lit(1)) == lit(1)
    assert absolute_value(lit(-1)) == lit(1)

    # Test for idempotence.
    assert absolute_value(absolute_value(lit(1))) == absolute_value(lit(1))
    assert absolute_value(absolute_value(lit(-1))) == absolute_value(lit(-1))

    # Test for Bools
    assert absolute_value(TRUE) == TRUE
    assert absolute_value(FALSE) == FALSE

    pytest.raises(ValueError, absolute_value, 0)


def test_lits():
    assert lits(cnf([[1, -2], [3, TRUE], [FALSE]])) == frozenset(
        {1, -2, 3, TRUE, FALSE}
    )


def test_tautologically_reduce_clause():
    trc = tautologically_reduce_clause  # local alias for long function name
    assert trc(clause([lit(1), TRUE])) == clause([TRUE])
    assert trc(clause([FALSE])) == clause([FALSE])
    assert trc(clause([lit(1), FALSE])) == clause([lit(1)])
    assert trc(clause([lit(1), lit(-1)])) == clause([TRUE])

    # Test for idempotence
    _clause = clause([lit(1), lit(-2), lit(3), lit(3)])
    assert trc(trc(_clause)) == trc(_clause)

    pytest.raises(ValueError, trc, set())


def test_tautologically_reduce_cnf():
    trc = tautologically_reduce_cnf  # local alias for long function name
    # cases where Clause reductions appear within Cnf reductions
    assert trc(cnf([[1, TRUE], [1, 2]])) == cnf([[1, 2]])
    assert trc(cnf([[FALSE], [1, 2]])) == cnf([[FALSE]])
    assert trc(cnf([[1, FALSE], [1, 2]])) == cnf([[1], [1, 2]])
    assert trc(cnf([[1, -1], [1, 2]])) == cnf([[1, 2]])

    # cases where we might have two simultaneous clause reductions
    assert trc(cnf([[1, TRUE], [FALSE]])) == cnf([[FALSE]])
    assert trc(cnf([[1, TRUE], [1, FALSE]])) == cnf([[1]])
    assert trc(cnf([[1, TRUE], [1, -1]])) == cnf([[TRUE]])
    assert trc(cnf([[FALSE], [1, FALSE]])) == cnf([[FALSE]])
    assert trc(cnf([[FALSE], [1, -1]])) == cnf([[FALSE]])
    assert trc(cnf([[1, FALSE], [1, -1]])) == cnf([[1]])

    # cases where we might have a cnf-related tautology
    assert trc(cnf([[1], [FALSE]])) == cnf([[FALSE]])
    assert trc(cnf([[TRUE]])) == cnf([[TRUE]])
    assert trc(cnf([[1], [TRUE]])) == cnf([[1]])

    # Test for idempotence.
    _cnf = cnf([[lit(1), lit(2)], [lit(-2)]])
    assert trc(trc(_cnf)) == trc(_cnf)

    pytest.raises(ValueError, trc, set())
    pytest.raises(ValueError, trc, frozenset())


def test_assign_variable_in_lit():
    avil = assign_variable_in_lit  # local alias for long function name

    assert avil(1, 1, TRUE) == TRUE
    assert avil(1, 1, FALSE) == FALSE
    assert avil(-1, 1, TRUE) == FALSE
    assert avil(-1, 1, FALSE) == TRUE
    assert avil(1, 2, TRUE) == 1
    assert avil(TRUE, 1, TRUE) == TRUE
    assert avil(FALSE, 1, TRUE) == FALSE

    # Test for idempotence
    assert avil(avil(1, 1, TRUE), 1, TRUE) == avil(1, 1, TRUE)
    assert avil(avil(-1, 1, TRUE), 1, TRUE) == avil(-1, 1, TRUE)


def test_assign_variable_in_clause():
    avic = assign_variable_in_clause  # local alias for long function name

    assert avic(clause([1, -2]), 1, TRUE) == {TRUE}
    assert avic(clause([1, -2]), 1, FALSE) == {-2}
    assert avic(clause([1, -2, -1]), 1, TRUE) == {TRUE}
    assert avic(clause([1, -2, -1]), 1, FALSE) == {TRUE}
    assert avic(clause([1, -2]), 2, TRUE) == {1}
    assert avic(clause([1, -2]), 2, FALSE) == {TRUE}
    assert avic(clause([1, -2, -1]), 2, TRUE) == {TRUE}
    assert avic(clause([1, -2, -1]), 2, FALSE) == {TRUE}

    # Test for idempotence
    _clause: Clause = clause([lit(1), lit(-2), lit(-1)])
    _var: Variable = variable(2)
    assert avic(avic(_clause, _var, FALSE), _var, FALSE) == avic(_clause, _var, FALSE)

    pytest.raises(ValueError, assign_variable_in_clause, [], 1, TRUE)


def test_assign_variable_in_cnf():
    avic = assign_variable_in_cnf  # local alias for long function name

    assert avic(cnf([[1, -2], [-1, 3]]), 1, TRUE) == cnf([[3]])
    assert avic(cnf([[1, -2], [-1, 3]]), 1, FALSE) == cnf([[-2]])

    # Test for idempotence.
    _cnf = cnf([[1, -2], [-1, 3]])
    assert avic(avic(_cnf, 1, FALSE), 1, FALSE) == avic(_cnf, 1, FALSE)

    pytest.raises(ValueError, avic, [[]], 1, TRUE)


def test_assign():
    assert assign(cnf([[1, -2], [-1, 3]]), {1: TRUE}) == cnf([[3]])
    assert assign(cnf([[1, -2], [-1, 3]]), {1: TRUE, 2: FALSE}) == cnf([[3]])
    assert assign(cnf([[1, -2], [-1, 3]]), {1: TRUE, 2: FALSE, 3: FALSE}) == cnf(
        [[FALSE]]
    )
    assert assign(cnf([[TRUE]]), {1: TRUE}) == cnf([[TRUE]])
    assert assign(cnf([[TRUE]]), {}) == cnf([[TRUE]])
    assert assign(cnf([[FALSE]]), {}) == cnf([[FALSE]])
    assert assign(cnf([[1]]), {}) == cnf([[1]])

    # Test for idempotence.
    _cnf = cnf([[1, -2], [-1, 3]])
    assert assign(assign(_cnf, {1: TRUE}), {1: TRUE}) == assign(_cnf, {1: TRUE})

    pytest.raises(ValueError, assign, [[]], {1: TRUE})

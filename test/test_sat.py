#! /usr/bin/env python3

import pytest
from ..sat import *

def test_generate_assignments():
    TRUE = cnf.TRUE
    FALSE = cnf.FALSE
    assert {1: TRUE} in generate_assignments(cnf.cnf([[1]]))
    assert {1: FALSE} in generate_assignments(cnf.cnf([[1]]))
    assert {1: TRUE} in generate_assignments(cnf.cnf([[-1]]))
    assert {1: FALSE} in generate_assignments(cnf.cnf([[-1]]))
    assert {} in generate_assignments(cnf.cnf([[TRUE]]))
    assert {} in generate_assignments(cnf.cnf([[FALSE]]))
    assert {1: TRUE, 2: TRUE} in generate_assignments(cnf.cnf([[1, -2]]))
    assert {1: TRUE, 2: FALSE} in generate_assignments(cnf.cnf([[1, -2]]))
    assert {1: FALSE, 2: TRUE} in generate_assignments(cnf.cnf([[1, -2]]))
    assert {1: FALSE, 2: FALSE} in generate_assignments(cnf.cnf([[1, -2]]))
    assert {} in generate_assignments(cnf.cnf([[1, -1]]))
    assert {} in generate_assignments(cnf.cnf([[1, -1]]))
    with pytest.raises(ValueError):
        generate_assignments(cnf.cnf([[]]))


def test_cnf_bruteforce_satcheck():
    TRUE = cnf.TRUE
    FALSE = cnf.FALSE
    satchecker = cnf_bruteforce_satcheck
    assert satchecker(cnf.cnf([[TRUE]]))
    assert not satchecker(cnf.cnf([[FALSE]]))
    assert satchecker(cnf.cnf([[1]]))
    assert satchecker(cnf.cnf([[-1]]))
    assert satchecker(cnf.cnf([[1], [TRUE]]))
    assert not satchecker(cnf.cnf([[1], [FALSE]]))
    assert satchecker(cnf.cnf([[1, FALSE]]))
    assert not satchecker(cnf.cnf([[1], [-1]]))
    assert not satchecker(cnf.cnf([[1, 2], [1, -2], [-1, 2], [-1, -2]]))
    assert not satchecker(cnf.cnf([[1, 2], [-1, 2], [-2, 3], [-2, -3]]))
    assert not satchecker(cnf.cnf([[1, 2], [1, -2], [-1, 2], [-1, 3], [-2, -3]]))


def test_cnf_pysat_satcheck():
    TRUE = cnf.TRUE
    FALSE = cnf.FALSE
    satchecker = cnf_pysat_satcheck
    assert satchecker(cnf.cnf([[TRUE]]))
    assert not satchecker(cnf.cnf([[FALSE]]))
    assert satchecker(cnf.cnf([[1]]))
    assert satchecker(cnf.cnf([[-1]]))
    assert satchecker(cnf.cnf([[1], [TRUE]]))
    assert not satchecker(cnf.cnf([[1], [FALSE]]))
    assert satchecker(cnf.cnf([[1, FALSE]]))
    assert not satchecker(cnf.cnf([[1], [-1]]))
    assert not satchecker(cnf.cnf([[1, 2], [1, -2], [-1, 2], [-1, -2]]))
    assert not satchecker(cnf.cnf([[1, 2], [-1, 2], [-2, 3], [-2, -3]]))
    assert not satchecker(cnf.cnf([[1, 2], [1, -2], [-1, 2], [-1, 3], [-2, -3]]))


def test_cnf_minisat_satcheck():
    TRUE = cnf.TRUE
    FALSE = cnf.FALSE
    satchecker = cnf_minisat_satcheck
    assert satchecker(cnf.cnf([[TRUE]]))
    assert not satchecker(cnf.cnf([[FALSE]]))
    assert satchecker(cnf.cnf([[1]]))
    assert satchecker(cnf.cnf([[-1]]))
    assert satchecker(cnf.cnf([[1], [TRUE]]))
    assert not satchecker(cnf.cnf([[1], [FALSE]]))
    assert satchecker(cnf.cnf([[1, FALSE]]))
    assert not satchecker(cnf.cnf([[1], [-1]]))
    assert not satchecker(cnf.cnf([[1, 2], [1, -2], [-1, 2], [-1, -2]]))
    assert not satchecker(cnf.cnf([[1, 2], [-1, 2], [-2, 3], [-2, -3]]))
    assert not satchecker(cnf.cnf([[1, 2], [1, -2], [-1, 2], [-1, 3], [-2, -3]]))


def test_literals_from_vertex():
    # Typical example
    assert literals_from_vertex(1) == (1, -1)


def test_clauses_from_hedge():
    # Typical example with isolated vertex.
    assert set(clauses_from_hedge({1})) == {cnf.clause([1]), cnf.clause([-1])}
    # Typical example with edge of size=2.
    assert set(clauses_from_hedge({1, 2})) == {cnf.clause([1, 2]), cnf.clause([1, -2]),
                                               cnf.clause([-1, 2]), cnf.clause([-1, -2])}


def test_cnfs_from_hedge():
    # Typical example with isolated vertex, multiplicity=1.
    assert set(cnfs_from_hedge([1], 1)) == {cnf.cnf([[1]]), cnf.cnf([[-1]])}

    # Typical example with isolated vertex, multiplicity=2.
    assert list(cnfs_from_hedge([1], 2)) == [cnf.cnf([[1], [-1]])]

    with pytest.raises(ValueError):
        cnfs_from_hedge([1], 3) #  exceeds possible multiplicity

    # Typical example with edge of size=2, multiplicity=1.
    assert set(cnfs_from_hedge({1, 2}, 1)) == {cnf.cnf([[1, 2]]),
                                               cnf.cnf([[1, -2]]),
                                               cnf.cnf([[-1, 2]]),
                                               cnf.cnf([[-1, -2]])}

    # Typical example with edge of size=2, multiplicity=1.
    assert set(cnfs_from_hedge({1, 2}, 2)) == {cnf.cnf([[1, 2], [1, -2]]),
                                               cnf.cnf([[1, 2], [-1, 2]]),
                                               cnf.cnf([[1, 2], [-1, -2]]),
                                               cnf.cnf([[1, -2], [-1, 2]]),
                                               cnf.cnf([[1, -2], [-1, -2]]),
                                               cnf.cnf([[-1, 2], [-1, -2]])}

    # Typical example with edge of size=2, multiplicity=3.
    assert set(cnfs_from_hedge({1, 2}, 3)) == {cnf.cnf([[1, 2], [1, -2], [-1, 2]]),
                                               cnf.cnf([[1, 2], [1, -2], [-1, -2]]),
                                               cnf.cnf([[1, 2], [-1, 2], [-1, -2]]),
                                               cnf.cnf([[1, -2], [-1, 2], [-1, -2]])}

    # Typical example with edge of size=2, multiplicity=4.
    assert list(cnfs_from_hedge({1, 2}, 4)) == [cnf.cnf([[1, 2], [1, -2], [-1, 2], [-1, -2]])]

    with pytest.raises(ValueError):
        cnfs_from_hedge({1, 2}, 0)  # zero multplicity raises error.
    with pytest.raises(ValueError):
        cnfs_from_hedge({1, 2}, 5)  # exceeds allowed multiplicity.


def test_cnfs_from_mhgraph():
    # Typical example with edge of size=1.
    assert set(cnfs_from_mhgraph(mhgraph.mhgraph([[1]]))) == set(cnfs_from_hedge({1}, 1))
    assert set(cnfs_from_mhgraph(mhgraph.mhgraph([[1], [1]]))) == set(cnfs_from_hedge({1}, 2))

    # Typical example with edge of size=2.
    assert set(cnfs_from_mhgraph(mhgraph.mhgraph([[1, 2]]))) == set(cnfs_from_hedge({1, 2}, 1))
    assert set(cnfs_from_mhgraph(mhgraph.mhgraph([[1, 2], [1, 2]]))) == set(cnfs_from_hedge({1, 2}, 2))
    assert set(cnfs_from_mhgraph(mhgraph.mhgraph([[1, 2], [1, 2], [1, 2]]))) \
        == set(cnfs_from_hedge({1, 2}, 3))
    assert list(cnfs_from_mhgraph(mhgraph.mhgraph([[1, 2], [1, 2], [1, 2], [1, 2]]))) \
        == [cnf.cnf([[1, 2], [1, -2], [-1, 2], [-1, -2]])]

    with pytest.raises(ValueError):
        cnfs_from_mhgraph(mhgraph.mhgraph(mhgraph.counter({frozenset({1, 2}): 5})))
    with pytest.raises(ValueError):
        cnfs_from_mhgraph(mhgraph.mhgraph(mhgraph.counter({frozenset({1, 2, 3}): 9})))


def test_mhgraph_bruteforce_satcheck():
    satchecker = mhgraph_bruteforce_satcheck
    assert satchecker(mhgraph.mhgraph([[1]]))
    assert not satchecker(mhgraph.mhgraph([[1], [1]]))
    assert satchecker(mhgraph.mhgraph([[1, 2]]))
    assert satchecker(mhgraph.mhgraph([[1, 2], [1, 2]]))
    assert satchecker(mhgraph.mhgraph([[1, 2], [1, 2], [1, 2]]))
    assert not satchecker(mhgraph.mhgraph([[1, 2], [1, 2], [1, 2], [1, 2]]))

    # K4 is unsat.
    assert not satchecker(mhgraph.mhgraph([[1, 2], [1, 3], [1, 4], [2, 3], [2, 4], [3, 4]]))

    # The following tests take longer and can be uncommented if we still wish to check them.
    # Butterfly is unsat
    assert not satchecker(mhgraph.mhgraph([[1, 2], [1, 3], [2, 3], [2, 4], [2, 5], [4, 5]]))
    # Bowtie is unsat
    #assert not satchecker(mhgraph.mhgraph([[1, 2], [1, 3], [2, 3], [2, 4], [4, 5], [4, 6],
    #                                       [5, 6]]))
    # 3-Book is unsat
    #assert not satchecker(mhgraph.mhgraph([[1, 2], [1, 3], [2, 3], [1, 4], [2, 4], [1, 5],
    #                                       [2, 5]]))

    assert not satchecker(mhgraph.mhgraph([[1, 2], [1, 2], [1, 2], [1, 3], [2, 3]]))
    assert not satchecker(mhgraph.mhgraph([[1, 2], [1, 2], [2, 3], [2, 3]]))
    assert not satchecker(mhgraph.mhgraph([[1, 2], [1, 2], [2, 3], [2, 4], [3, 4]]))
    assert not satchecker(mhgraph.mhgraph([[1, 2], [1, 2], [1, 3], [1, 4], [2, 3], [2, 4]]))

    assert satchecker(mhgraph.mhgraph([[1, 2, 3]]))
    assert not satchecker(mhgraph.mhgraph(mhgraph.counter({frozenset({1, 2, 3}): 8})))


def test_mhgraph_pysat_satcheck():
    satchecker = mhgraph_pysat_satcheck
    assert satchecker(mhgraph.mhgraph([[1]]))
    assert not satchecker(mhgraph.mhgraph([[1], [1]]))
    assert satchecker(mhgraph.mhgraph([[1, 2]]))
    assert satchecker(mhgraph.mhgraph([[1, 2], [1, 2]]))
    assert satchecker(mhgraph.mhgraph([[1, 2], [1, 2], [1, 2]]))
    assert not satchecker(mhgraph.mhgraph([[1, 2], [1, 2], [1, 2], [1, 2]]))

    # K4 is unsat.
    assert not satchecker(mhgraph.mhgraph([[1, 2], [1, 3], [1, 4], [2, 3], [2, 4], [3, 4]]))

    # Butterfly is unsat
    assert not satchecker(mhgraph.mhgraph([[1, 2], [1, 3], [2, 3], [2, 4], [2, 5], [4, 5]]))
    # Bowtie is unsat
    assert not satchecker(mhgraph.mhgraph([[1, 2], [1, 3], [2, 3], [2, 4], [4, 5], [4, 6],
                                           [5, 6]]))
    # 3-Book is unsat
    assert not satchecker(mhgraph.mhgraph([[1, 2], [1, 3], [2, 3], [1, 4], [2, 4], [1, 5],
                                           [2, 5]]))

    assert not satchecker(mhgraph.mhgraph([[1, 2], [1, 2], [1, 2], [1, 3], [2, 3]]))
    assert not satchecker(mhgraph.mhgraph([[1, 2], [1, 2], [2, 3], [2, 3]]))
    assert not satchecker(mhgraph.mhgraph([[1, 2], [1, 2], [2, 3], [2, 4], [3, 4]]))
    assert not satchecker(mhgraph.mhgraph([[1, 2], [1, 2], [1, 3], [1, 4], [2, 3], [2, 4]]))

    assert satchecker(mhgraph.mhgraph([[1, 2, 3]]))
    assert not satchecker(mhgraph.mhgraph(mhgraph.counter({frozenset({1, 2, 3}): 8})))


def test_mhgraph_minisat_satcheck():
    """
    satchecker = mhgraph_minisat_satcheck
    assert mhgraph_minisat_satcheck(mhgraph.mhgraph([[1]]))
    assert not satchecker(mhgraph.mhgraph([[1], [1]]))
    assert satchecker(mhgraph.mhgraph([[1, 2]]))
    assert satchecker(mhgraph.mhgraph([[1, 2], [1, 2]]))
    assert satchecker(mhgraph.mhgraph([[1, 2], [1, 2], [1, 2]]))
    assert not satchecker(mhgraph.mhgraph([[1, 2], [1, 2], [1, 2], [1, 2]]))

    # K4 is unsat.
    assert not satchecker(mhgraph.mhgraph([[1, 2], [1, 3], [1, 4], [2, 3], [2, 4], [3, 4]]))

    # The following tests take longer and can be uncommented if we still wish to check them.
    # Butterfly is unsat
    assert not satchecker(mhgraph.mhgraph([[1, 2], [1, 3], [2, 3], [2, 4], [2, 5], [4, 5]]))
    # Bowtie is unsat
    #assert not satchecker(mhgraph.mhgraph([[1, 2], [1, 3], [2, 3], [2, 4], [4, 5], [4, 6],
    #                                       [5, 6]]))
    # 3-Book is unsat
    #assert not satchecker(mhgraph.mhgraph([[1, 2], [1, 3], [2, 3], [1, 4], [2, 4], [1, 5],
    #                                       [2, 5]]))

    assert not satchecker(mhgraph.mhgraph([[1, 2], [1, 2], [1, 2], [1, 3], [2, 3]]))
    assert not satchecker(mhgraph.mhgraph([[1, 2], [1, 2], [2, 3], [2, 3]]))
    assert not satchecker(mhgraph.mhgraph([[1, 2], [1, 2], [2, 3], [2, 4], [3, 4]]))
    assert not satchecker(mhgraph.mhgraph([[1, 2], [1, 2], [1, 3], [1, 4], [2, 3], [2, 4]]))

    assert satchecker(mhgraph.mhgraph([[1, 2, 3]]))
    assert not satchecker(mhgraph.mhgraph(mhgraph.counter({frozenset({1, 2, 3}): 8})))
    """


def test_mhgraph_from_cnf():
    with pytest.raises(ValueError):
        mhgraph_from_cnf(cnf.cnf([[cnf.TRUE]]))
    with pytest.raises(ValueError):
        mhgraph_from_cnf(cnf.cnf([[cnf.FALSE]]))
    with pytest.raises(ValueError):
        mhgraph_from_cnf(cnf.cnf([[1, -1]]))
    with pytest.raises(ValueError):
        mhgraph_from_cnf(cnf.cnf([[1, cnf.TRUE]]))
    with pytest.raises(ValueError):
        mhgraph_from_cnf(cnf.cnf([[1], [cnf.FALSE]]))

    assert mhgraph_from_cnf(cnf.cnf([[1]])) == mhgraph.mhgraph([[1]])
    assert mhgraph_from_cnf(cnf.cnf([[1, cnf.FALSE]])) == mhgraph.mhgraph([[1]])
    assert mhgraph_from_cnf(cnf.cnf([[1], [cnf.TRUE]])) == mhgraph.mhgraph([[1]])
    assert mhgraph_from_cnf(cnf.cnf([[1, 2]])) == mhgraph.mhgraph([[1, 2]])
    assert mhgraph_from_cnf(cnf.cnf([[-1, 2]])) == mhgraph.mhgraph([[1, 2]])
    assert mhgraph_from_cnf(cnf.cnf([[-1, -2]])) == mhgraph.mhgraph([[1, 2]])
    assert mhgraph_from_cnf(cnf.cnf([[1], [1, -2]])) == mhgraph.mhgraph([[1], [1, 2]])
    assert mhgraph_from_cnf(cnf.cnf([[1, 2], [1, -2]])) == mhgraph.mhgraph([[1, 2], [1, 2]])

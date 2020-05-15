#! /usr/bin/env python3
import pytest
import cnf
from sat import *

cc = cnf.cnf
mhg = mhgraph.mhgraph


def test_generate_assignments():
    TRUE = cnf.TRUE
    FALSE = cnf.FALSE
    assert {1: TRUE} in generate_assignments(cc([[1]]))
    assert {1: FALSE} in generate_assignments(cc([[1]]))
    assert {1: TRUE} in generate_assignments(cc([[-1]]))
    assert {1: FALSE} in generate_assignments(cc([[-1]]))
    assert {} in generate_assignments(cc([[TRUE]]))
    assert {} in generate_assignments(cc([[FALSE]]))
    assert {1: TRUE, 2: TRUE} in generate_assignments(cc([[1, -2]]))
    assert {1: TRUE, 2: FALSE} in generate_assignments(cc([[1, -2]]))
    assert {1: FALSE, 2: TRUE} in generate_assignments(cc([[1, -2]]))
    assert {1: FALSE, 2: FALSE} in generate_assignments(cc([[1, -2]]))
    assert {} in generate_assignments(cc([[1, -1]]))
    assert {} in generate_assignments(cc([[1, -1]]))
    with pytest.raises(ValueError):
        generate_assignments(cc([[]]))


def test_cnf_bruteforce_satcheck():
    TRUE = cnf.TRUE
    FALSE = cnf.FALSE
    satchecker = cnf_bruteforce_satcheck
    assert satchecker(cc([[TRUE]]))
    assert not satchecker(cc([[FALSE]]))
    assert satchecker(cc([[1]]))
    assert satchecker(cc([[-1]]))
    assert satchecker(cc([[1], [TRUE]]))
    assert not satchecker(cc([[1], [FALSE]]))
    assert satchecker(cc([[1, FALSE]]))
    assert not satchecker(cc([[1], [-1]]))
    assert not satchecker(cc([[1, 2], [1, -2], [-1, 2], [-1, -2]]))
    assert not satchecker(cc([[1, 2], [-1, 2], [-2, 3], [-2, -3]]))
    assert not satchecker(cc([[1, 2], [1, -2], [-1, 2], [-1, 3], [-2, -3]]))


def test_cnf_pysat_satcheck():
    TRUE = cnf.TRUE
    FALSE = cnf.FALSE
    satchecker = cnf_pysat_satcheck
    assert satchecker(cc([[TRUE]]))
    assert satchecker(cc([[TRUE], [TRUE, FALSE]]))
    assert not satchecker(cc([[FALSE]]))
    assert satchecker(cc([[1]]))
    assert satchecker(cc([[-1]]))
    assert satchecker(cc([[1], [TRUE]]))
    assert not satchecker(cc([[1], [FALSE]]))
    assert satchecker(cc([[1, FALSE]]))
    assert not satchecker(cc([[1], [-1]]))
    assert not satchecker(cc([[1, 2], [1, -2], [-1, 2], [-1, -2]]))
    assert not satchecker(cc([[1, 2], [-1, 2], [-2, 3], [-2, -3]]))
    assert not satchecker(cc([[1, 2], [1, -2], [-1, 2], [-1, 3], [-2, -3]]))


def test_cnf_minisat_satcheck():
    TRUE = cnf.TRUE
    FALSE = cnf.FALSE
    satchecker = cnf_minisat_satcheck
    assert satchecker(cc([[TRUE]]))
    assert not satchecker(cc([[FALSE]]))
    assert satchecker(cc([[1]]))
    assert satchecker(cc([[-1]]))
    assert satchecker(cc([[1], [TRUE]]))
    assert not satchecker(cc([[1], [FALSE]]))
    assert satchecker(cc([[1, FALSE]]))
    assert not satchecker(cc([[1], [-1]]))
    assert not satchecker(cc([[1, 2], [1, -2], [-1, 2], [-1, -2]]))
    assert not satchecker(cc([[1, 2], [-1, 2], [-2, 3], [-2, -3]]))
    assert not satchecker(cc([[1, 2], [1, -2], [-1, 2], [-1, 3], [-2, -3]]))


def test_lits_from_vertex():
    # Typical example
    assert lits_from_vertex(1) == (1, -1)


def test_clauses_from_hedge():
    # Typical example with isolated vertex.
    assert set(clauses_from_hedge({1})) == {cnf.clause([1]), cnf.clause([-1])}
    # Typical example with edge of size=2.
    assert set(clauses_from_hedge({1, 2})) == {cnf.clause([1, 2]), cnf.clause([1, -2]),
                                               cnf.clause([-1, 2]), cnf.clause([-1, -2])}


def test_cnfs_from_hedge():
    # Typical example with isolated vertex, multiplicity=1.
    assert set(cnfs_from_hedge([1], 1)) == {cc([[1]]), cc([[-1]])}

    # Typical example with isolated vertex, multiplicity=2.
    assert list(cnfs_from_hedge([1], 2)) == [cc([[1], [-1]])]

    assert not list(cnfs_from_hedge([1], 3)) #  exceeds possible multiplicity

    # Typical example with edge of size=2, multiplicity=1.
    assert set(cnfs_from_hedge({1, 2}, 1)) == {cc([[1, 2]]),
                                               cc([[1, -2]]),
                                               cc([[-1, 2]]),
                                               cc([[-1, -2]])}

    # Typical example with edge of size=2, multiplicity=1.
    assert set(cnfs_from_hedge({1, 2}, 2)) == {cc([[1, 2], [1, -2]]),
                                               cc([[1, 2], [-1, 2]]),
                                               cc([[1, 2], [-1, -2]]),
                                               cc([[1, -2], [-1, 2]]),
                                               cc([[1, -2], [-1, -2]]),
                                               cc([[-1, 2], [-1, -2]])}

    # Typical example with edge of size=2, multiplicity=3.
    assert set(cnfs_from_hedge({1, 2}, 3)) == {cc([[1, 2], [1, -2], [-1, 2]]),
                                               cc([[1, 2], [1, -2], [-1, -2]]),
                                               cc([[1, 2], [-1, 2], [-1, -2]]),
                                               cc([[1, -2], [-1, 2], [-1, -2]])}

    # Typical example with edge of size=2, multiplicity=4.
    assert list(cnfs_from_hedge({1, 2}, 4)) == [cc([[1, 2], [1, -2], [-1, 2], [-1, -2]])]

    with pytest.raises(ValueError):  # zero multplicity. Raises ValueError when making CNFs.
        list(cnfs_from_hedge({1, 2}, 0))
    assert not list(cnfs_from_hedge({1, 2}, 5)) # exceeds allowed multiplicity.


def test_cnfs_from_mhgraph():
    # Typical example with edge of size=1.
    assert set(cnfs_from_mhgraph(mhg([[1]]))) == set(cnfs_from_hedge({1}, 1))
    assert set(cnfs_from_mhgraph(mhg([[1], [1]]))) == set(cnfs_from_hedge({1}, 2))

    # Typical example with edge of size=2.
    assert set(cnfs_from_mhgraph(mhg([[1, 2]]))) == set(cnfs_from_hedge({1, 2}, 1))
    assert set(cnfs_from_mhgraph(mhg([[1, 2], [1, 2]]))) == set(cnfs_from_hedge({1, 2}, 2))
    assert set(cnfs_from_mhgraph(mhg([[1, 2], [1, 2], [1, 2]]))) \
        == set(cnfs_from_hedge({1, 2}, 3))
    assert list(cnfs_from_mhgraph(mhg([[1, 2], [1, 2], [1, 2], [1, 2]]))) \
        == [cc([[1, 2], [1, -2], [-1, 2], [-1, -2]])]

    assert not list(cnfs_from_mhgraph(mhg(mhgraph.counter({frozenset({1, 2}): 5}))))
    assert not list(cnfs_from_mhgraph(mhg(mhgraph.counter({frozenset({1, 2, 3}): 9}))))


def test_number_of_cnfs():
    assert number_of_cnfs(mhg([[1]])) == 2
    assert number_of_cnfs(mhg([[1]]*2)) == 1
    assert number_of_cnfs(mhg([[1]]*3)) == 0
    
    assert number_of_cnfs(mhg([[1, 2]])) == 4
    assert number_of_cnfs(mhg([[1, 2]]*2)) == 6
    assert number_of_cnfs(mhg([[1, 2]]*3)) == 4
    assert number_of_cnfs(mhg([[1, 2]]*4)) == 1
    assert number_of_cnfs(mhg([[1, 2]]*5)) == 0

    assert number_of_cnfs(mhg([[1, 2, 3]])) == 8
    


def test_mhgraph_bruteforce_satcheck():
    satchecker = mhgraph_bruteforce_satcheck
    assert satchecker(mhg([[1]]))
    assert not satchecker(mhg([[1], [1]]))
    assert satchecker(mhg([[1, 2]]))
    assert satchecker(mhg([[1, 2], [1, 2]]))
    assert satchecker(mhg([[1, 2], [1, 2], [1, 2]]))
    assert not satchecker(mhg([[1, 2], [1, 2], [1, 2], [1, 2]]))

    # K4 is unsat.
    assert not satchecker(mhg([[1, 2], [1, 3], [1, 4], [2, 3], [2, 4], [3, 4]]))

    # The following tests take longer and can be uncommented if we still wish to check them.
    # Butterfly is unsat
    assert not satchecker(mhg([[1, 2], [1, 3], [2, 3], [2, 4], [2, 5], [4, 5]]))
    # Bowtie is unsat
    #assert not satchecker(mhg([[1, 2], [1, 3], [2, 3], [2, 4], [4, 5], [4, 6],
    #                                       [5, 6]]))
    # 3-Book is unsat
    #assert not satchecker(mhg([[1, 2], [1, 3], [2, 3], [1, 4], [2, 4], [1, 5],
    #                                       [2, 5]]))

    assert not satchecker(mhg([[1, 2], [1, 2], [1, 2], [1, 3], [2, 3]]))
    assert not satchecker(mhg([[1, 2], [1, 2], [2, 3], [2, 3]]))
    assert not satchecker(mhg([[1, 2], [1, 2], [2, 3], [2, 4], [3, 4]]))
    assert not satchecker(mhg([[1, 2], [1, 2], [1, 3], [1, 4], [2, 3], [2, 4]]))

    assert satchecker(mhg([[1, 2, 3]]))
    assert not satchecker(mhg(mhgraph.counter({frozenset({1, 2, 3}): 8})))


def test_mhgraph_pysat_satcheck():
    satchecker = mhgraph_pysat_satcheck
    assert satchecker(mhg([[1]]*1))
    assert not satchecker(mhg([[1]]*2))
    assert not satchecker(mhg([[1]]*3))
    assert not satchecker(mhg([[1]]*4))

    assert satchecker(mhg([[1, 2]]))
    assert satchecker(mhg([[1, 2], [1, 2]]))
    assert satchecker(mhg([[1, 2], [1, 2], [1, 2]]))
    assert not satchecker(mhg([[1, 2], [1, 2], [1, 2], [1, 2]]))

    # K4 is unsat.
    assert not satchecker(mhg([[1, 2], [1, 3], [1, 4], [2, 3], [2, 4], [3, 4]]))

    # Butterfly is unsat
    assert not satchecker(mhg([[1, 2], [1, 3], [2, 3], [2, 4], [2, 5], [4, 5]]))
    # Bowtie is unsat
    assert not satchecker(mhg([[1, 2], [1, 3], [2, 3], [2, 4], [4, 5], [4, 6],
                                           [5, 6]]))
    # 3-Book is unsat
    assert not satchecker(mhg([[1, 2], [1, 3], [2, 3], [1, 4], [2, 4], [1, 5],
                                           [2, 5]]))

    assert not satchecker(mhg([[1, 2], [1, 2], [1, 2], [1, 3], [2, 3]]))
    assert not satchecker(mhg([[1, 2], [1, 2], [2, 3], [2, 3]]))
    assert not satchecker(mhg([[1, 2], [1, 2], [2, 3], [2, 4], [3, 4]]))
    assert not satchecker(mhg([[1, 2], [1, 2], [1, 3], [1, 4], [2, 3], [2, 4]]))

    assert satchecker(mhg([[1, 2, 3]]))
    assert not satchecker(mhg(mhgraph.counter({frozenset({1, 2, 3}): 8})))

@pytest.mark.xfail(reason='This spawns subprocesses which eat up memory.')
def test_mhgraph_minisat_satcheck():
    satchecker = mhgraph_minisat_satcheck
    assert mhgraph_minisat_satcheck(mhg([[1]]))
    assert not satchecker(mhg([[1], [1]]))
    assert satchecker(mhg([[1, 2]]))
    assert satchecker(mhg([[1, 2], [1, 2]]))
    assert satchecker(mhg([[1, 2], [1, 2], [1, 2]]))
    assert not satchecker(mhg([[1, 2], [1, 2], [1, 2], [1, 2]]))

    # K4 is unsat.
    assert not satchecker(mhg([[1, 2], [1, 3], [1, 4], [2, 3], [2, 4], [3, 4]]))

    # The following tests take longer and can be uncommented if we still wish to check them.
    # Butterfly is unsat
    assert not satchecker(mhg([[1, 2], [1, 3], [2, 3], [2, 4], [2, 5], [4, 5]]))
    # Bowtie is unsat
    #assert not satchecker(mhg([[1, 2], [1, 3], [2, 3], [2, 4], [4, 5], [4, 6],
    #                                       [5, 6]]))
    # 3-Book is unsat
    #assert not satchecker(mhg([[1, 2], [1, 3], [2, 3], [1, 4], [2, 4], [1, 5],
    #                                       [2, 5]]))

    assert not satchecker(mhg([[1, 2], [1, 2], [1, 2], [1, 3], [2, 3]]))
    assert not satchecker(mhg([[1, 2], [1, 2], [2, 3], [2, 3]]))
    assert not satchecker(mhg([[1, 2], [1, 2], [2, 3], [2, 4], [3, 4]]))
    assert not satchecker(mhg([[1, 2], [1, 2], [1, 3], [1, 4], [2, 3], [2, 4]]))

    assert satchecker(mhg([[1, 2, 3]]))
    assert not satchecker(mhg(mhgraph.counter({frozenset({1, 2, 3}): 8})))


def test_mhgraph_from_cnf():
    with pytest.raises(ValueError):
        mhgraph_from_cnf(cc([[cnf.TRUE]]))
    with pytest.raises(ValueError):
        mhgraph_from_cnf(cc([[cnf.FALSE]]))
    with pytest.raises(ValueError):
        mhgraph_from_cnf(cc([[1, -1]]))
    with pytest.raises(ValueError):
        mhgraph_from_cnf(cc([[1, cnf.TRUE]]))
    with pytest.raises(ValueError):
        mhgraph_from_cnf(cc([[1], [cnf.FALSE]]))

    assert mhgraph_from_cnf(cc([[1]])) == mhg([[1]])
    assert mhgraph_from_cnf(cc([[1, cnf.FALSE]])) == mhg([[1]])
    assert mhgraph_from_cnf(cc([[1], [cnf.TRUE]])) == mhg([[1]])
    assert mhgraph_from_cnf(cc([[1, 2]])) == mhg([[1, 2]])
    assert mhgraph_from_cnf(cc([[-1, 2]])) == mhg([[1, 2]])
    assert mhgraph_from_cnf(cc([[-1, -2]])) == mhg([[1, 2]])
    assert mhgraph_from_cnf(cc([[1], [1, -2]])) == mhg([[1], [1, 2]])
    assert mhgraph_from_cnf(cc([[1, 2], [1, -2]])) == mhg([[1, 2], [1, 2]])


def test_simplify_at_loops():
    assert simplify_at_loops(mhg([[1]]))
    assert not simplify_at_loops(mhg([[1]]*2))
    assert not simplify_at_loops(mhg([[1]]*3))
    assert not simplify_at_loops(mhg([[1]]*4))
    
    assert simplify_at_loops(mhg([[1], [1, 2]]))
    assert simplify_at_loops(mhg([[1], [2, 3]])) == mhg([[2, 3]])
    assert not simplify_at_loops(mhg([[1], [1, 2], [2]]))
    assert simplify_at_loops(mhg([[1, 2]])) == mhg([[1, 2]])

    assert simplify_at_loops(mhg([[1, 2]]*4)) == mhg([[1, 2]]*4)
    assert simplify_at_loops(mhg([[1, 2]]*5)) == mhg([[1, 2]]*5)

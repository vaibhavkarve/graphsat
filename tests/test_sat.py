#! /usr/bin/env python3.8

from collections import Counter as counter

import pytest

from graphsat.cnf import Bool, clause, cnf, lit
from graphsat.graph import vertex
from graphsat.mhgraph import HEdge, MHGraph, hedge, mhgraph
from graphsat.sat import (clauses_from_hedge, cnf_bruteforce_satcheck,
                          cnf_minisat_satcheck, cnf_pysat_satcheck,
                          cnfs_from_hedge, cnfs_from_mhgraph,
                          generate_assignments, is_oversaturated,
                          lits_from_vertex, mhgraph_bruteforce_satcheck,
                          mhgraph_from_cnf, mhgraph_minisat_satcheck,
                          mhgraph_pysat_satcheck)

mm = mhgraph
cc = cnf

def test_generate_assignments() -> None:
    assert {1: Bool.TRUE} in list(generate_assignments(cc([[1]])))
    assert {1: Bool.FALSE} in list(generate_assignments(cc([[1]])))
    assert {1: Bool.TRUE} in list(generate_assignments(cc([[-1]])))
    assert {1: Bool.FALSE} in list(generate_assignments(cc([[-1]])))
    assert list(generate_assignments(cc([[Bool.TRUE]]))) == [{}]
    assert list(generate_assignments(cc([[Bool.FALSE]]))) == [{}]
    assert {1: Bool.TRUE, 2: Bool.TRUE} in list(generate_assignments(cc([[1, -2]])))
    assert {1: Bool.TRUE, 2: Bool.FALSE} in list(generate_assignments(cc([[1, -2]])))
    assert {1: Bool.FALSE, 2: Bool.TRUE} in list(generate_assignments(cc([[1, -2]])))
    assert {1: Bool.FALSE, 2: Bool.FALSE} in list(generate_assignments(cc([[1, -2]])))
    assert list(generate_assignments(cc([[1, -1]]))) == [{}]
    assert list(generate_assignments(cc([[1, -1]]))) == [{}]
    with pytest.raises(ValueError):
        list(generate_assignments(cc([[]])))


def test_cnf_bruteforce_satcheck() -> None:
    satchecker = cnf_bruteforce_satcheck
    assert satchecker(cc([[Bool.TRUE]]))
    assert not satchecker(cc([[Bool.FALSE]]))
    assert satchecker(cc([[1]]))
    assert satchecker(cc([[-1]]))
    assert satchecker(cc([[1], [Bool.TRUE]]))
    assert not satchecker(cc([[1], [Bool.FALSE]]))
    assert satchecker(cc([[1, Bool.FALSE]]))
    assert not satchecker(cc([[1], [-1]]))
    assert not satchecker(cc([[1, 2], [1, -2], [-1, 2], [-1, -2]]))
    assert not satchecker(cc([[1, 2], [-1, 2], [-2, 3], [-2, -3]]))
    assert not satchecker(cc([[1, 2], [1, -2], [-1, 2], [-1, 3], [-2, -3]]))


def test_cnf_pysat_satcheck() -> None:
    satchecker = cnf_pysat_satcheck
    assert satchecker(cc([[Bool.TRUE]]))
    assert not satchecker(cc([[Bool.FALSE]]))
    assert satchecker(cc([[1]]))
    assert satchecker(cc([[-1]]))
    assert satchecker(cc([[1], [Bool.TRUE]]))
    assert not satchecker(cc([[1], [Bool.FALSE]]))
    assert satchecker(cc([[1, Bool.FALSE]]))
    assert not satchecker(cc([[1], [-1]]))
    assert not satchecker(cc([[1, 2], [1, -2], [-1, 2], [-1, -2]]))
    assert not satchecker(cc([[1, 2], [-1, 2], [-2, 3], [-2, -3]]))
    assert not satchecker(cc([[1, 2], [1, -2], [-1, 2], [-1, 3], [-2, -3]]))


def test_cnf_minisat_satcheck() -> None:
    satchecker = cnf_minisat_satcheck
    assert satchecker(cc([[Bool.TRUE]]))
    assert not satchecker(cc([[Bool.FALSE]]))
    assert satchecker(cc([[1]]))
    assert satchecker(cc([[-1]]))
    assert satchecker(cc([[1], [Bool.TRUE]]))
    assert not satchecker(cc([[1], [Bool.FALSE]]))
    assert satchecker(cc([[1, Bool.FALSE]]))
    assert not satchecker(cc([[1], [-1]]))
    assert not satchecker(cc([[1, 2], [1, -2], [-1, 2], [-1, -2]]))
    assert not satchecker(cc([[1, 2], [-1, 2], [-2, 3], [-2, -3]]))
    assert not satchecker(cc([[1, 2], [1, -2], [-1, 2], [-1, 3], [-2, -3]]))


def test_literals_from_vertex() -> None:
    # Typical example
    assert lits_from_vertex(vertex(1)) == (lit(1), lit(-1))


def test_clauses_from_hedge() -> None:
    # Typical example with isolated vertex.
    assert set(clauses_from_hedge(hedge((1,)))) == {clause([1]), clause([-1])}
    # Typical example with edge of size=2.
    assert set(clauses_from_hedge(hedge((1, 2)))) == {clause([1, 2]), clause([1, -2]),
                                                      clause([-1, 2]), clause([-1, -2])}


def test_cnfs_from_hedge() -> None:
    # Typical example with isolated vertex, multiplicity=1.
    assert set(cnfs_from_hedge(hedge([1]), 1)) == {cc([[1]]), cc([[-1]])}

    # Typical example with isolated vertex, multiplicity=2.
    assert list(cnfs_from_hedge(hedge([1]), 2)) == [cc([[1], [-1]])]

    assert not list(cnfs_from_hedge(hedge([1]), 3)) #  exceeds possible multiplicity

    # Typical example with edge of size=2, multiplicity=1.
    assert set(cnfs_from_hedge(hedge({1, 2}), 1)) == {cc([[1, 2]]),
                                               cc([[1, -2]]),
                                               cc([[-1, 2]]),
                                               cc([[-1, -2]])}

    # Typical example with edge of size=2, multiplicity=1.
    assert set(cnfs_from_hedge(hedge({1, 2}), 2)) == {cc([[1, 2], [1, -2]]),
                                               cc([[1, 2], [-1, 2]]),
                                               cc([[1, 2], [-1, -2]]),
                                               cc([[1, -2], [-1, 2]]),
                                               cc([[1, -2], [-1, -2]]),
                                               cc([[-1, 2], [-1, -2]])}

    # Typical example with edge of size=2, multiplicity=3.
    assert set(cnfs_from_hedge(hedge({1, 2}), 3)) == {cc([[1, 2], [1, -2], [-1, 2]]),
                                               cc([[1, 2], [1, -2], [-1, -2]]),
                                               cc([[1, 2], [-1, 2], [-1, -2]]),
                                               cc([[1, -2], [-1, 2], [-1, -2]])}

    # Typical example with edge of size=2, multiplicity=4.
    assert list(cnfs_from_hedge(hedge({1, 2}), 4)) == [cc([[1, 2], [1, -2], [-1, 2], [-1, -2]])]

    with pytest.raises(ValueError):  # zero multplicity. Raises ValueError when making CNFs.
        list(cnfs_from_hedge(hedge({1, 2}), 0))
    assert not list(cnfs_from_hedge(hedge({1, 2}), 5)) # exceeds allowed multiplicity.


@pytest.mark.parametrize(
    'mhgraph,hedge,multiplicity',
    [([[1]], {1}, 1),
     ([[1]]*2, {1}, 2),
     ([[1]]*3, {1}, 3),
     ([[1, 2]], {1, 2}, 1),
     ([[1, 2]]*2, {1, 2}, 2),
     ([[1, 2]]*3, {1, 2}, 3),
     ([[1, 2]]*4, {1, 2}, 4),
     ([[1, 2]]*5, {1, 2}, 5),
     ([[1, 2, 3]]*9, {1, 2}, 9)])
def test_cnfs_from_mhgraph(mhgraph: MHGraph, hedge: HEdge, multiplicity: int) -> None:
    assert set(cnfs_from_mhgraph(mm(mhgraph))) == set(cnfs_from_hedge(hedge, multiplicity))



def test_mhgraph_bruteforce_satcheck() -> None:
    satchecker = mhgraph_bruteforce_satcheck
    assert satchecker(mm([[1]]))
    assert not satchecker(mm([[1], [1]]))
    assert satchecker(mm([[1, 2]]))
    assert satchecker(mm([[1, 2], [1, 2]]))
    assert satchecker(mm([[1, 2], [1, 2], [1, 2]]))
    assert not satchecker(mm([[1, 2], [1, 2], [1, 2], [1, 2]]))

    # K4 is unsat.
    assert not satchecker(mm([[1, 2], [1, 3], [1, 4], [2, 3], [2, 4], [3, 4]]))

    # The following tests take longer and can be uncommented if we still wish to check them.
    # Butterfly is unsat
    assert not satchecker(mm([[1, 2], [1, 3], [2, 3], [2, 4], [2, 5], [4, 5]]))
    # Bowtie is unsat
    #assert not satchecker(mm([[1, 2], [1, 3], [2, 3], [2, 4], [4, 5], [4, 6],
    #                                       [5, 6]]))
    # 3-Book is unsat
    #assert not satchecker(mm([[1, 2], [1, 3], [2, 3], [1, 4], [2, 4], [1, 5],
    #                                       [2, 5]]))

    assert not satchecker(mm([[1, 2], [1, 2], [1, 2], [1, 3], [2, 3]]))
    assert not satchecker(mm([[1, 2], [1, 2], [2, 3], [2, 3]]))
    assert not satchecker(mm([[1, 2], [1, 2], [2, 3], [2, 4], [3, 4]]))
    assert not satchecker(mm([[1, 2], [1, 2], [1, 3], [1, 4], [2, 3], [2, 4]]))

    assert satchecker(mm([[1, 2, 3]]))
    assert not satchecker(mm(counter({frozenset({1, 2, 3}): 8})))


def test_mhgraph_pysat_satcheck() -> None:
    satchecker = mhgraph_pysat_satcheck
    assert satchecker(mm([[1]]))
    assert not satchecker(mm([[1]]*2))
    assert not satchecker(mm([[1]]*3))


    assert satchecker(mm([[1, 2]]*1))
    assert satchecker(mm([[1, 2]]*2))
    assert satchecker(mm([[1, 2]]*3))
    assert not satchecker(mm([[1, 2]]*4))
    assert not satchecker(mm([[1, 2]]*5))
    assert not satchecker(mm([[1, 2]]*6))

    # K4-e is unsat
    assert satchecker(mm([[1, 2], [1, 3], [1, 4], [2, 3], [2, 4]]))
    # K4 is unsat.
    assert not satchecker(mm([[1, 2], [1, 3], [1, 4], [2, 3], [2, 4], [3, 4]]))
    # Butterfly is unsat
    assert not satchecker(mm([[1, 2], [1, 3], [2, 3], [2, 4], [2, 5], [4, 5]]))
    # Bowtie is unsat
    assert not satchecker(mm([[1, 2], [1, 3], [2, 3], [2, 4], [4, 5], [4, 6], [5,
                                                                               6]]))
    # 3-Book is unsat
    assert not satchecker(mm([[1, 2], [1, 3], [2, 3], [1, 4], [2, 4], [1, 5], [2,
                                                                               5]]))

    assert not satchecker(mm([[1, 2], [1, 2], [1, 2], [1, 3], [2, 3]]))
    assert not satchecker(mm([[1, 2], [1, 2], [2, 3], [2, 3]]))
    assert not satchecker(mm([[1, 2], [1, 2], [2, 3], [2, 4], [3, 4]]))
    assert not satchecker(mm([[1, 2], [1, 2], [1, 3], [1, 4], [2, 3], [2, 4]]))

    assert satchecker(mm([[1, 2, 3]]))
    assert not satchecker(mm(counter({frozenset({1, 2, 3}): 8})))


@pytest.mark.xfail(reason='This spawns subprocesses which eat up memory.')
def test_mhgraph_minisat_satcheck() -> None:
    satchecker = mhgraph_minisat_satcheck
    assert mhgraph_minisat_satcheck(mm([[1]]))
    assert not satchecker(mm([[1], [1]]))
    assert satchecker(mm([[1, 2]]))
    assert satchecker(mm([[1, 2], [1, 2]]))
    assert satchecker(mm([[1, 2], [1, 2], [1, 2]]))
    assert not satchecker(mm([[1, 2], [1, 2], [1, 2], [1, 2]]))

    # K4 is unsat.
    assert not satchecker(mm([[1, 2], [1, 3], [1, 4], [2, 3], [2, 4], [3, 4]]))

    # The following tests take longer and can be uncommented if we still wish to check them.
    # Butterfly is unsat
    assert not satchecker(mm([[1, 2], [1, 3], [2, 3], [2, 4], [2, 5], [4, 5]]))
    # Bowtie is unsat
    #assert not satchecker(mm([[1, 2], [1, 3], [2, 3], [2, 4], [4, 5], [4, 6],
    #                                       [5, 6]]))
    # 3-Book is unsat
    #assert not satchecker(mm([[1, 2], [1, 3], [2, 3], [1, 4], [2, 4], [1, 5],
    #                                       [2, 5]]))

    assert not satchecker(mm([[1, 2], [1, 2], [1, 2], [1, 3], [2, 3]]))
    assert not satchecker(mm([[1, 2], [1, 2], [2, 3], [2, 3]]))
    assert not satchecker(mm([[1, 2], [1, 2], [2, 3], [2, 4], [3, 4]]))
    assert not satchecker(mm([[1, 2], [1, 2], [1, 3], [1, 4], [2, 3], [2, 4]]))

    assert satchecker(mm([[1, 2, 3]]))
    assert not satchecker(mm(counter({frozenset({1, 2, 3}): 8})))


def test_mhgraph_from_cnf() -> None:
    with pytest.raises(ValueError):
        mhgraph_from_cnf(cc([[Bool.TRUE]]))
    with pytest.raises(ValueError):
        mhgraph_from_cnf(cc([[Bool.FALSE]]))
    with pytest.raises(ValueError):
        mhgraph_from_cnf(cc([[1, -1]]))
    with pytest.raises(ValueError):
        mhgraph_from_cnf(cc([[1, Bool.TRUE]]))
    with pytest.raises(ValueError):
        mhgraph_from_cnf(cc([[1], [Bool.FALSE]]))

    assert mhgraph_from_cnf(cc([[1]])) == mm([[1]])
    assert mhgraph_from_cnf(cc([[1, Bool.FALSE ]])) == mm([[1]])
    assert mhgraph_from_cnf(cc([[1], [Bool.TRUE]])) == mm([[1]])
    assert mhgraph_from_cnf(cc([[1, 2]])) == mm([[1, 2]])
    assert mhgraph_from_cnf(cc([[-1, 2]])) == mm([[1, 2]])
    assert mhgraph_from_cnf(cc([[-1, -2]])) == mm([[1, 2]])
    assert mhgraph_from_cnf(cc([[1], [1, -2]])) == mm([[1], [1, 2]])
    assert mhgraph_from_cnf(cc([[1, 2], [1, -2]])) == mm([[1, 2], [1, 2]])


def test_is_oversaturated() -> None:
    assert not is_oversaturated(mm([[1]]))
    assert not is_oversaturated(mm([[1]]*2))
    assert is_oversaturated(mm([[1]]*3))

    assert not is_oversaturated(mm([[1, 2]]*3))
    assert not is_oversaturated(mm([[1, 2]]*4))
    assert is_oversaturated(mm([[1, 2]]*5))

    assert not is_oversaturated(mm([[1, 2, 3]]*7))
    assert not is_oversaturated(mm([[1, 2, 3]]*8))
    assert is_oversaturated(mm([[1, 2, 3]]*9))

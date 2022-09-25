#! /usr/bin/env python3.8

from collections import Counter as counter
from normal_form.cnf import Bool, clause, cnf, lit

import pytest

from graphsat.graph import vertex
from graphsat.mhgraph import HEdge, MHGraph, hedge, mhgraph
from graphsat.translation import (clauses_from_hedge, cnfs_from_hedge,
                                  cnfs_from_mhgraph, is_oversaturated,
                                  lits_from_vertex,
                                  mhgraph_bruteforce_satcheck,
                                  mhgraph_from_cnf,
                                  mhgraph_minisat_satcheck,
                                  mhgraph_pysat_satcheck)


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
    assert set(cnfs_from_hedge(hedge([1]), 1)) == {cnf([[1]]), cnf([[-1]])}

    # Typical example with isolated vertex, multiplicity=2.
    assert list(cnfs_from_hedge(hedge([1]), 2)) == [cnf([[1], [-1]])]

    assert not list(cnfs_from_hedge(hedge([1]), 3)) #  exceeds possible multiplicity

    # Typical example with edge of size=2, multiplicity=1.
    assert set(cnfs_from_hedge(hedge({1, 2}), 1)) == {cnf([[1, 2]]),
                                               cnf([[1, -2]]),
                                               cnf([[-1, 2]]),
                                               cnf([[-1, -2]])}

    # Typical example with edge of size=2, multiplicity=1.
    assert set(cnfs_from_hedge(hedge({1, 2}), 2)) == {cnf([[1, 2], [1, -2]]),
                                               cnf([[1, 2], [-1, 2]]),
                                               cnf([[1, 2], [-1, -2]]),
                                               cnf([[1, -2], [-1, 2]]),
                                               cnf([[1, -2], [-1, -2]]),
                                               cnf([[-1, 2], [-1, -2]])}

    # Typical example with edge of size=2, multiplicity=3.
    assert set(cnfs_from_hedge(hedge({1, 2}), 3)) == {cnf([[1, 2], [1, -2], [-1, 2]]),
                                               cnf([[1, 2], [1, -2], [-1, -2]]),
                                               cnf([[1, 2], [-1, 2], [-1, -2]]),
                                               cnf([[1, -2], [-1, 2], [-1, -2]])}

    # Typical example with edge of size=2, multiplicity=4.
    assert list(cnfs_from_hedge(hedge({1, 2}), 4)) == [cnf([[1, 2], [1, -2], [-1, 2], [-1, -2]])]

    with pytest.raises(ValueError):  # zero multplicity. Raises ValueError when making CNFs.
        list(cnfs_from_hedge(hedge({1, 2}), 0))
    assert not list(cnfs_from_hedge(hedge({1, 2}), 5)) # exceeds allowed multiplicity.


@pytest.mark.parametrize(
    'mhgraph_instance,hedge,multiplicity',
    [([[1]], {1}, 1),
     ([[1]]*2, {1}, 2),
     ([[1]]*3, {1}, 3),
     ([[1, 2]], {1, 2}, 1),
     ([[1, 2]]*2, {1, 2}, 2),
     ([[1, 2]]*3, {1, 2}, 3),
     ([[1, 2]]*4, {1, 2}, 4),
     ([[1, 2]]*5, {1, 2}, 5),
     ([[1, 2, 3]]*9, {1, 2}, 9)])
def test_cnfs_from_mhgraph(mhgraph_instance: MHGraph, hedge: HEdge, multiplicity: int) -> None:
    assert set(cnfs_from_mhgraph(mhgraph(mhgraph_instance))) \
        == set(cnfs_from_hedge(hedge, multiplicity))



def test_mhgraph_bruteforce_satcheck() -> None:
    satchecker = mhgraph_bruteforce_satcheck
    assert satchecker(mhgraph([[1]]))
    assert not satchecker(mhgraph([[1], [1]]))
    assert satchecker(mhgraph([[1, 2]]))
    assert satchecker(mhgraph([[1, 2], [1, 2]]))
    assert satchecker(mhgraph([[1, 2], [1, 2], [1, 2]]))
    assert not satchecker(mhgraph([[1, 2], [1, 2], [1, 2], [1, 2]]))

    # K4 is unsat.
    assert not satchecker(mhgraph([[1, 2], [1, 3], [1, 4], [2, 3], [2, 4], [3, 4]]))

    # The following tests take longer and can be uncommented if we still wish to check them.
    # Butterfly is unsat
    assert not satchecker(mhgraph([[1, 2], [1, 3], [2, 3], [2, 4], [2, 5], [4, 5]]))
    # Bowtie is unsat
    #assert not satchecker(mhgraph([[1, 2], [1, 3], [2, 3], [2, 4], [4, 5], [4, 6],
    #                                       [5, 6]]))
    # 3-Book is unsat
    #assert not satchecker(mhgraph([[1, 2], [1, 3], [2, 3], [1, 4], [2, 4], [1, 5],
    #                                       [2, 5]]))

    assert not satchecker(mhgraph([[1, 2], [1, 2], [1, 2], [1, 3], [2, 3]]))
    assert not satchecker(mhgraph([[1, 2], [1, 2], [2, 3], [2, 3]]))
    assert not satchecker(mhgraph([[1, 2], [1, 2], [2, 3], [2, 4], [3, 4]]))
    assert not satchecker(mhgraph([[1, 2], [1, 2], [1, 3], [1, 4], [2, 3], [2, 4]]))

    assert satchecker(mhgraph([[1, 2, 3]]))
    assert not satchecker(mhgraph(counter({frozenset({1, 2, 3}): 8})))


def test_mhgraph_pysat_satcheck() -> None:
    satchecker = mhgraph_pysat_satcheck
    assert satchecker(mhgraph([[1]]))
    assert not satchecker(mhgraph([[1]]*2))
    assert not satchecker(mhgraph([[1]]*3))


    assert satchecker(mhgraph([[1, 2]]*1))
    assert satchecker(mhgraph([[1, 2]]*2))
    assert satchecker(mhgraph([[1, 2]]*3))
    assert not satchecker(mhgraph([[1, 2]]*4))
    assert not satchecker(mhgraph([[1, 2]]*5))
    assert not satchecker(mhgraph([[1, 2]]*6))

    # K4-e is unsat
    assert satchecker(mhgraph([[1, 2], [1, 3], [1, 4], [2, 3], [2, 4]]))
    # K4 is unsat.
    assert not satchecker(mhgraph([[1, 2], [1, 3], [1, 4], [2, 3], [2, 4], [3, 4]]))
    # Butterfly is unsat
    assert not satchecker(mhgraph([[1, 2], [1, 3], [2, 3], [2, 4], [2, 5], [4, 5]]))
    # Bowtie is unsat
    assert not satchecker(mhgraph([[1, 2], [1, 3], [2, 3], [2, 4], [4, 5], [4, 6], [5,
                                                                               6]]))
    # 3-Book is unsat
    assert not satchecker(mhgraph([[1, 2], [1, 3], [2, 3], [1, 4], [2, 4], [1, 5], [2,
                                                                               5]]))

    assert not satchecker(mhgraph([[1, 2], [1, 2], [1, 2], [1, 3], [2, 3]]))
    assert not satchecker(mhgraph([[1, 2], [1, 2], [2, 3], [2, 3]]))
    assert not satchecker(mhgraph([[1, 2], [1, 2], [2, 3], [2, 4], [3, 4]]))
    assert not satchecker(mhgraph([[1, 2], [1, 2], [1, 3], [1, 4], [2, 3], [2, 4]]))

    assert satchecker(mhgraph([[1, 2, 3]]))
    assert not satchecker(mhgraph(counter({frozenset({1, 2, 3}): 8})))


@pytest.mark.xfail(reason='This spawns subprocesses which eat up memory.')
def test_mhgraph_minisat_satcheck() -> None:
    satchecker = mhgraph_minisat_satcheck
    assert mhgraph_minisat_satcheck(mhgraph([[1]]))
    assert not satchecker(mhgraph([[1], [1]]))
    assert satchecker(mhgraph([[1, 2]]))
    assert satchecker(mhgraph([[1, 2], [1, 2]]))
    assert satchecker(mhgraph([[1, 2], [1, 2], [1, 2]]))
    assert not satchecker(mhgraph([[1, 2], [1, 2], [1, 2], [1, 2]]))

    # K4 is unsat.
    assert not satchecker(mhgraph([[1, 2], [1, 3], [1, 4], [2, 3], [2, 4], [3, 4]]))

    # The following tests take longer and can be uncommented if we still wish to check them.
    # Butterfly is unsat
    assert not satchecker(mhgraph([[1, 2], [1, 3], [2, 3], [2, 4], [2, 5], [4, 5]]))
    # Bowtie is unsat
    #assert not satchecker(mhgraph([[1, 2], [1, 3], [2, 3], [2, 4], [4, 5], [4, 6],
    #                                       [5, 6]]))
    # 3-Book is unsat
    #assert not satchecker(mhgraph([[1, 2], [1, 3], [2, 3], [1, 4], [2, 4], [1, 5],
    #                                       [2, 5]]))

    assert not satchecker(mhgraph([[1, 2], [1, 2], [1, 2], [1, 3], [2, 3]]))
    assert not satchecker(mhgraph([[1, 2], [1, 2], [2, 3], [2, 3]]))
    assert not satchecker(mhgraph([[1, 2], [1, 2], [2, 3], [2, 4], [3, 4]]))
    assert not satchecker(mhgraph([[1, 2], [1, 2], [1, 3], [1, 4], [2, 3], [2, 4]]))

    assert satchecker(mhgraph([[1, 2, 3]]))
    assert not satchecker(mhgraph(counter({frozenset({1, 2, 3}): 8})))


def test_mhgraph_from_cnf() -> None:
    with pytest.raises(ValueError):
        mhgraph_from_cnf(cnf([[Bool.TRUE]]))
    with pytest.raises(ValueError):
        mhgraph_from_cnf(cnf([[Bool.FALSE]]))
    with pytest.raises(ValueError):
        mhgraph_from_cnf(cnf([[1, -1]]))
    with pytest.raises(ValueError):
        mhgraph_from_cnf(cnf([[1, Bool.TRUE]]))
    with pytest.raises(ValueError):
        mhgraph_from_cnf(cnf([[1], [Bool.FALSE]]))

    assert mhgraph_from_cnf(cnf([[1]])) == mhgraph([[1]])
    assert mhgraph_from_cnf(cnf([[1, Bool.FALSE ]])) == mhgraph([[1]])
    assert mhgraph_from_cnf(cnf([[1], [Bool.TRUE]])) == mhgraph([[1]])
    assert mhgraph_from_cnf(cnf([[1, 2]])) == mhgraph([[1, 2]])
    assert mhgraph_from_cnf(cnf([[-1, 2]])) == mhgraph([[1, 2]])
    assert mhgraph_from_cnf(cnf([[-1, -2]])) == mhgraph([[1, 2]])
    assert mhgraph_from_cnf(cnf([[1], [1, -2]])) == mhgraph([[1]])
    assert mhgraph_from_cnf(cnf([[1, 2], [1, -2]])) == mhgraph([[1, 2], [1, 2]])


def test_is_oversaturated() -> None:
    assert not is_oversaturated(mhgraph([[1]]))
    assert not is_oversaturated(mhgraph([[1]]*2))
    assert is_oversaturated(mhgraph([[1]]*3))

    assert not is_oversaturated(mhgraph([[1, 2]]*3))
    assert not is_oversaturated(mhgraph([[1, 2]]*4))
    assert is_oversaturated(mhgraph([[1, 2]]*5))

    assert not is_oversaturated(mhgraph([[1, 2, 3]]*7))
    assert not is_oversaturated(mhgraph([[1, 2, 3]]*8))
    assert is_oversaturated(mhgraph([[1, 2, 3]]*9))

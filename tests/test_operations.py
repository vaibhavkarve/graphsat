#! /usr/bin/env python3.8


from graphsat.mhgraph import mhgraph
from graphsat.operations import sat_and, satg
from normal_form.sxpr import AtomicSxpr, SatSxpr


def test_satg() -> None:
    assert satg(True)
    assert not satg(False)

    assert satg(mhgraph([[1, 2]]))
    assert satg(mhgraph([[1, 2]]*2))
    assert satg(mhgraph([[1, 2]]*3))
    assert not satg(mhgraph([[1, 2]]*4))

    assert satg(AtomicSxpr(sat_and, (True,)))
    assert not satg(AtomicSxpr(sat_and, (True, False)))
    assert satg(AtomicSxpr(sat_and, (mhgraph([[1]]),)))
    assert not satg(AtomicSxpr(sat_and, (mhgraph([[1]]), mhgraph([[1]]*2))))
    assert satg(SatSxpr(sat_and, (True,)))

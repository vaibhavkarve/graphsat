#! /usr/bin/env python3

import pytest
from operations import *
from mhgraph import mhgraph as mhg
from sxpr import AtomicSxpr, SatSxpr, Sxpr

def test_graph_union():
    assert graph_union(mhg([[1, 2], [3]]), mhg([[1, 11]])) ==  mhg([[1, 2], [3], [1, 11]])


def test_satg():
    assert satg(True)
    assert not satg(False)

    assert satg(mhg([[1, 2]]))
    assert satg(mhg([[1, 2]]*2))
    assert satg(mhg([[1, 2]]*3))
    assert not satg(mhg([[1, 2]]*4))

    assert satg(AtomicSxpr(sat_and, (True,)))
    assert not satg(AtomicSxpr(sat_and, (True, False)))
    assert satg(AtomicSxpr(sat_and, (mhg([[1]]),)))
    assert not satg(AtomicSxpr(sat_and, (mhg([[1]]), mhg([[1]]*2))))
    assert satg(SatSxpr(sat_and, (True,)))

    with pytest.raises(TypeError):
        assert satg(Sxpr(sat_and, (True,), True))



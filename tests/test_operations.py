#! /usr/bin/env python3.9

import pytest
from operations import *
from mhgraph import mhgraph
from sxpr import AtomicSxpr, SatSxpr, Sxpr


def test_satg():
    assert satg(True)
    assert not satg(False)

    #assert satg(mhgraph([[1, 2]]))
    #assert satg(mhgraph([[1, 2]]*2))
    #assert satg(mhgraph([[1, 2]]*3))
    #assert not satg(mhgraph([[1, 2]]*4))

    assert satg(AtomicSxpr(sat_and, (True,)))
    assert not satg(AtomicSxpr(sat_and, (True, False)))
    assert satg(AtomicSxpr(sat_and, (mhgraph([[1]]),)))
    assert not satg(AtomicSxpr(sat_and, (mhgraph([[1]]), mhgraph([[1]]*2))))
    assert satg(SatSxpr(sat_and, (True,)))

    with pytest.raises(TypeError):
        assert satg(Sxpr(sat_and, (True,), True))

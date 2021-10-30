#! /usr/bin/env python3.8

import pytest
from graphsat.mhgraph import mhgraph as mhg
from graphsat.operations import sat_and, sat_or
from graphsat.sxpr import AtomicSxpr, Sxpr, SatSxpr


def test_Sxpr():
    assert Sxpr(lambda x, y: x+y, (1, 2, 3, 4), 0).reduce() == 10
    assert Sxpr(lambda x, y: x+y, (1, 2, 3, 4), 100).reduce() == 110
    assert Sxpr(lambda x, b: x**2 if b else x, (True, True, False, True), 2).reduce() == 256


def test_SatSxpr():
    # empty arguments
    assert SatSxpr(sat_and, ()).reduce()
    assert not SatSxpr(sat_or, ()).reduce()

    # boolean arguments
    assert SatSxpr(sat_and, (True, True, True)).reduce()
    assert not SatSxpr(sat_and, (True, True, False)).reduce()
    assert not SatSxpr(sat_and, (True, False, True)).reduce()
    assert not SatSxpr(sat_and, (False, True, True)).reduce()

    assert not SatSxpr(sat_or, (False, False, False)).reduce()
    assert SatSxpr(sat_or, (True, True, False)).reduce()
    assert SatSxpr(sat_or, (True, False, True)).reduce()
    assert SatSxpr(sat_or, (False, True, True)).reduce()
    assert not SatSxpr(sat_or, (False, False)).reduce()

    # MHGraph arguments
    assert SatSxpr(sat_and, (mhg([[1]]), mhg([[2]]), mhg([[3]]))).reduce()
    assert not SatSxpr(sat_and, (mhg([[1]]), mhg([[2]]*2), mhg([[3]]))).reduce()
    assert not SatSxpr(sat_or, (mhg([[1]]*2), mhg([[2]]*2))).reduce()
    assert SatSxpr(sat_or, (mhg([[1]]), mhg([[2]]*2), mhg([[3]]))).reduce()

    g2 = mhg([[2]]*2)
    g3 = mhg([[2]]*3)
    assert not SatSxpr(sat_or, (g2, g2)).reduce()


def test_AtomicSxpr():
    # MHGraph arguments
    assert AtomicSxpr(sat_and, (mhg([[1]]), mhg([[2]]), mhg([[3]]))).reduce()
    assert not AtomicSxpr(sat_and, (mhg([[1]]), mhg([[2]]*2), mhg([[3]]))).reduce()
    assert not AtomicSxpr(sat_or, (mhg([[1]]*2), mhg([[2]]*2))).reduce()
    assert AtomicSxpr(sat_or, (mhg([[1]]), mhg([[2]]*2), mhg([[3]]))).reduce()

    with pytest.raises(ValueError):
        AtomicSxpr(lambda x, y: x and y, (True, False, True))

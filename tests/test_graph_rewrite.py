#!/usr/bin/env python3.8


from graphsat import mhgraph
from graphsat.graph_rewrite import decompose


def test_decompose() -> None:
    assert decompose(mhgraph.mhgraph([[1]]))
    assert not decompose(mhgraph.mhgraph([[1]]*2))
    assert not decompose(mhgraph.mhgraph([[1]]*3))


    assert decompose(mhgraph.mhgraph([[1, 2]]*1))
    assert decompose(mhgraph.mhgraph([[1, 2]]*2))
    assert decompose(mhgraph.mhgraph([[1, 2]]*3))
    assert not decompose(mhgraph.mhgraph([[1, 2]]*4))
    assert not decompose(mhgraph.mhgraph([[1, 2]]*5))
    assert not decompose(mhgraph.mhgraph([[1, 2]]*6))

    # K4-e is unsat
    assert decompose(mhgraph.mhgraph([[1, 2], [1, 3], [1, 4], [2, 3], [2, 4]]))
    # K4 is unsat.
    assert not decompose(mhgraph.mhgraph([[1, 2], [1, 3], [1, 4], [2, 3], [2, 4], [3, 4]]))
    # Butterfly is unsat
    assert not decompose(mhgraph.mhgraph([[1, 2], [1, 3], [2, 3], [2, 4], [2, 5], [4, 5]]))
    # Bowtie is unsat
    assert not decompose(mhgraph.mhgraph([[1, 2], [1, 3], [2, 3], [2, 4], [4, 5], [4, 6], [5, 6]]))
    # 3-Book is unsat
    assert not decompose(mhgraph.mhgraph([[1, 2], [1, 3], [2, 3], [1, 4], [2, 4], [1, 5], [2,
                                                                               5]]))

    assert not decompose(mhgraph.mhgraph([[1, 2], [1, 2], [1, 2], [1, 3], [2, 3]]))
    assert not decompose(mhgraph.mhgraph([[1, 2], [1, 2], [2, 3], [2, 3]]))
    assert not decompose(mhgraph.mhgraph([[1, 2], [1, 2], [2, 3], [2, 4], [3, 4]]))
    assert not decompose(mhgraph.mhgraph([[1, 2], [1, 2], [1, 3], [1, 4], [2, 3], [2, 4]]))

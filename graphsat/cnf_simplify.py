#!/usr/bin/env python3.8
"""Functions for simplifying Cnfs, particularly (a∨b∨c) ∧ (a∨b∨¬c) to (a∨b).

This simplification is traditionally handled by the Quine–McCluskey
algorithm. But for our simple use-case, this might be over-engineered.

Instead we implement our own functions for making this simplification.

"""
import itertools as it
from typing import FrozenSet, cast

from graphsat.cnf import cnf, Bool, Cnf, Clause, Lit, clause, absolute_value
import graphsat.mhgraph as mhg


#@ft.lru_cache
def hedge_of_clause(clause: Clause) -> mhg.HEdge:
    """Return the hedge corresponding to a clause.

    hedge_of_clause = hedge ∘ set ∘ map(absolute_value, __)

    """
    absolute_literal_values: set[int | Bool] = {absolute_value(literal).value for literal in clause}
    assert all(isinstance(value, int) for value in absolute_literal_values), "Encountered Bool value."
    return mhg.hedge(cast(set[int], absolute_literal_values))


def differing_lits(clause1: Clause, clause2: Clause) -> FrozenSet[Lit]:
    """Give a set of literals that two clauses differ on.

    This returns a set that can give us (2-times-of-the) Hamming distance between
    clauses. Assume that the clauses have the same image under `heade_of_clause`. If
    not, raise an AssertionError.

    Quick way to compute set of distinct lits is to calculate the symmetric
    difference between them (using the ^ operator).

    ∀ c : Clause,
       differing_lits(c, c) = ∅
    ∀ c d : Clause,
       differing_lits(c, d) = differing_lits(d, c)

    """
    assert hedge_of_clause(clause1) == hedge_of_clause(clause2)
    return clause1 ^ clause2


def equivalent_smaller_clause(clause1: Clause, clause2: Clause) -> Clause:
    """Given clauses that are distance 1 apart, return smaller equiv. clause.

    The smaller equivalent clause is given by the intersection of the two clauses.
    This is computed using the `&` operator.

    """
    assert len(differing_lits(clause1, clause2)) == 2, 'Hamming distance should be 1.'

    equiv_clause: Clause = clause(clause1 & clause2)
    assert len(equiv_clause) == len(clause1) - 1
    return equiv_clause


def reduce_distance_one_clauses(cnf_instance: Cnf) -> Cnf:
    """Reduce all clauses in the the

    The problem this function is trying to solve is known to be NP-hard. This is an
    inefficient solution to this problem. Do not apply it to Cnfs with more than 5
    variables.

    reduce_cnf = ungroup_clauses_to_cnf ∘ reduce_all_groups ∘ group_clauses_by_edge
    """
    for clause1, clause2 in it.combinations(cnf_instance, 2):
        hedge1: mhg.HEdge = hedge_of_clause(clause1)
        hedge2: mhg.HEdge = hedge_of_clause(clause2)
        if hedge1 == hedge2 and len(differing_lits(clause1, clause2)) == 2:
            # Hamming distance in clauses = 1
            reduced_cnf = cnf_instance - {clause1, clause2}
            reduced_cnf = reduced_cnf | {equivalent_smaller_clause(clause1, clause2)}
            return reduce_distance_one_clauses(cnf(reduced_cnf))
    return cnf_instance


def subclause_reduction(cnf_instance: Cnf) -> Cnf:
    """Replace the conjunction of two clauses with the smaller clause.

    If c₁ c₂ : Clause, we sat the c₁ ≪ c₂ if every literal of c₁ is in c₂.

    Replace c₁ ∧ c₂ with c₁ whenever c₁ ≪ c₂.
    Perform action recursively.
    """
    for clause1, clause2 in it.permutations(cnf_instance, 2):
        if clause1 <= clause2:
            new_cnf: Cnf = cnf(cnf_instance - {clause2})
            return subclause_reduction(new_cnf)
    return cnf_instance


def reduce_cnf(cnf_instance: Cnf) -> Cnf:
    """Reduce distance=1 as well as subclauses."""
    return subclause_reduction(reduce_distance_one_clauses(cnf_instance))



if __name__ == '__main__':  # pragma: no cover
    x: Cnf = cnf([[1, 2, -3], [1, 2, 3], [-1, -2, 3], [4, 5], [4, 5, -6]])
    print(reduce_cnf(x))

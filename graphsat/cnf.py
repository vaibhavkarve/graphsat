#!/usr/bin/env python3.10
"""Constructors and functions for sentences in conjunctive normal form (Cnf)."""

# Imports
# =======
from __future__ import annotations

import functools as ft
from collections.abc import Callable, Iterator
from enum import Enum
from typing import (Any, Collection, Final, Generator, Mapping, NewType,
                    TypeAlias, final)

from attrs import define
from loguru import logger

# Classes and Types
# =================
Variable = NewType("Variable", int)
Variable.__doc__ = """`Variable` is a subtype of `int`."""


@final
@ft.total_ordering
class Bool(Enum):
    FALSE = "F"
    TRUE = "T"

    def __lt__(self, other: Any) -> bool:
        if isinstance(other, int):
            return True
        if isinstance(other, Bool):
            return self.value < other.value
        return NotImplemented

    def __eq__(self, other: Any) -> bool:
        if isinstance(other, int):
            return False
        if isinstance(other, Bool):
            return self is other
        return NotImplemented

    def __hash__(self) -> int:
        return hash(self.value)



@define(eq=True, order=True, frozen=True)
class Lit:
    value: int | Bool

    def __repr__(self) -> str:
        return f"Lit({self.value})"



class Clause(frozenset[Lit]):  # pylint: disable=too-few-public-methods
    """`Clause` is a subclass of `frozenset[Lit]`."""
    def __repr__(self) -> str:
        sorted_lit_values: Generator[str, None, None] = (str(lit.value) for lit in sorted(self))
        return f"Clause({{{', '.join(sorted_lit_values)}}})"


class Cnf(frozenset[Clause]):  # pylint: disable=too-few-public-methods
    """`Cnf` is a subclass of `frozenset[Clause]`."""

    def __str__(self) -> str:
        """Pretty print a Cnf after sorting its sorted clause tuples."""
        sorted_clause_values: Iterator[str] = map(str, sorted(self))
        return f"Cnf({{{', '.join(sorted_clause_values)}}})"


Assignment: TypeAlias = Mapping[Variable, Bool]  # defines a type alias


# Constructor Functions
# =====================
def variable(positive_int: int | Variable) -> Variable:
    """Constructor-function for Variable type.

    By definition, a `Variable` is just a positive integer.  This
    function is idempotent.

    Args:
       positive_int (:obj:`int`):

    Return:
       If input is indeed positive, then return ``positive_int``
       after casting to Variable.

    Raises:
       ValueError: if ``positive_int <= 0``.
    """
    if positive_int <= 0:
        raise ValueError("Variable must be a positive integer.")
    return Variable(positive_int)


def lit(int_or_bool: int | Bool | Lit) -> Lit:
    match int_or_bool:
        case 0:
            raise ValueError("Lit must be a nonzero integer or Bool member.")
        case _ if isinstance(int_or_bool, Lit):
            return int_or_bool
        case _ if isinstance(int_or_bool, (int, Bool)):
            return Lit(int_or_bool)
        case _:
            raise TypeError("Lit must be either Bool or int.")
    raise TypeError("Lit must be either Bool or int.")


def clause(lit_collection: Collection[int | Bool | Lit]) -> Clause:
    """Constructor-function for Clause type.

    By definition, a `Clause` is a nonempty frozenset of Lits. This function is idempotent.

    Args:
       lit_collection (:obj:`Collection[int]`): a nonempty collection of ints.

    Return:
       Check that each element in the collection satisfies axioms for being a Lit and then cast
          to Clause.

    Raises:
       ValueError: if ``lit_collection`` is an empty collection.

    """
    if not lit_collection:
        raise ValueError(f"Encountered empty input {list(lit_collection)}.")
    return Clause(frozenset(map(lit, lit_collection)))


def cnf(clause_collection: Collection[Collection[int | Bool | Lit]]) -> Cnf:
    """Constructor-function for Cnf type.

    By definition, a `Cnf` is a nonempty frozenset of Clauses. This function is idempotent.

    Args:
       clause_collection (:obj:`Collection[Collection[int]]`): a nonempty collection (list,
          tuple, set, frozenset) of nonempty collections of integers or Bools.

    Return:
       Check that each element in the collection satisfies axioms for being a Clause and
          then cast to Cnf.

    Raises:
       ValueError: if ``clause_collection`` is an empty collection.
    """
    if not clause_collection:
        raise ValueError(f"Encountered empty input {list(clause_collection)}.")
    return Cnf(frozenset(map(clause, clause_collection)))


# Helpful Constants
# =================
TRUE_CLAUSE: Final[Clause] = clause([Bool.TRUE])
FALSE_CLAUSE: Final[Clause] = clause([Bool.FALSE])
TRUE_CNF: Final[Cnf] = cnf([TRUE_CLAUSE])
FALSE_CNF: Final[Cnf] = cnf([FALSE_CLAUSE])  # not documented, for internal use only


# Basic Functions
# ===============
def neg(literal: Lit) -> Lit:  # type: ignore
    """Negate a Lit.

    This function is an involution.

    Args:
       literal (:obj:`Lit`): a Lit formed from a nonzero integer or from a Bool.

    Return:
       Return the Lit cast from the negative of ``literal``. If ``literal`` is of type
          Bool, then return ``TRUE`` for ``FALSE``, ``FALSE`` for ``TRUE``.

    """
    match literal.value:
        case Bool.TRUE:
            return lit(Bool.FALSE)
        case Bool.FALSE:
            return lit(Bool.TRUE)
        case _ if isinstance(literal.value, int):
            return lit(- literal.value)
        case _:
            raise TypeError(f"Argument to neg should  be of type Lit. Found {literal = }.")


def absolute_value(literal: Lit) -> Lit:
    """Unnegated form of a Lit.

    This function is idempotent.

    Args:
       literal (:obj:`Lit`): a Lit formed from a nonzero integer.

    Return:
       Check that ``literal`` is not of type Bool and then return the absolute value of
          ``literal``. If it is of type Bool, then return ``literal`` as is.
    """
    if isinstance(literal.value, Bool):
        return lit(Bool.TRUE)
    return lit(abs(literal.value))


def lits(cnf_instance: Cnf) -> frozenset[Lit]:
    """Return frozenset of all Lits that appear in a Cnf.

    Args:
       cnf_instance (:obj:`Cnf`)

    Return:
       A frozenset of all lits that appear in a Cnf.
    """
    return frozenset.union(*cnf_instance)


# Functions for Simplification
# ============================
def tautologically_reduce_clause(clause_instance: Clause) -> Clause:
    r"""Reduce a Clause using various tautologies.

    The order in which these reductions are performed is important. This function is
    idempotent.

    Tautologies affecting Clauses:
       (⊤ ∨ c = ⊤)  (⊥ = ⊥)  (⊥ ∨ c = c)  (c ∨ ¬c = ⊤),
       where `x` is a Clause, `⊤` represents ``TRUE``, `⊥` represents ``FALSE``, and `∨` is
          disjunction.

    Args:
       clause_instance (:obj:`set[Lit]`): an abstract set (a set or a frozenset) of Lits.

    Return:
       The Clause formed by performing all the above-mentioned tautological reductions.
    """
    if lit(Bool.TRUE) in clause_instance:
        return TRUE_CLAUSE
    if set(clause_instance) == {lit(Bool.FALSE)}:
        return FALSE_CLAUSE
    if lit(Bool.FALSE) in clause_instance:
        clause_instance = clause(
            [literal for literal in clause_instance if literal != lit(Bool.FALSE)])
    if not set(map(neg, clause_instance)).isdisjoint(clause_instance):
        return TRUE_CLAUSE
    return clause(clause_instance)


def tautologically_reduce_cnf(cnf_instance: Cnf) -> Cnf:
    r"""Reduce a Cnf using various tautologies.

    The order in which these reductions are performed is important. This function is
    idempotent. This is a recursive function that is guaranteed to terminate.

    Tautologies affecting Cnfs:
       (x ∧ ⊥ = ⊥)  (⊤ = ⊤)  (⊤ ∧ x = x),
       where `x` is a Cnf, `⊤` represents ``TRUE``, `⊥` represents ``FALSE``, and `∧` is
       conjunction.

    Args:
       cnf_instance (:obj:`set[set[Lit]]`): an abstract set (set or frozenset) of abstract sets
       of Lits.

    Return:
       The Cnf formed by first reducing all the clauses tautologically and then performing all
       the above-mentioned tautological reductions on the Cnf itself.
    """
    clause_set_reduced: set[Clause]
    clause_set_reduced = set(map(tautologically_reduce_clause, cnf_instance))

    if FALSE_CLAUSE in clause_set_reduced:
        return FALSE_CNF
    if clause_set_reduced == set(TRUE_CNF):
        return TRUE_CNF
    if TRUE_CLAUSE in clause_set_reduced:
        return tautologically_reduce_cnf(cnf(clause_set_reduced - TRUE_CNF))
    return cnf(clause_set_reduced)


# Functions for Assignment
# ========================
def assign_variable_in_lit(
    literal: Lit, variable_instance: Variable, boolean: Bool
) -> Lit:
    """Assign Bool value to a Variable if present in Lit.

    Replace all instances of ``variable_instance`` and its negation with ``boolean`` and its
    negation respectively. Leave all else unchanged. This function is idempotent.

    Args:
       literal (:obj:`Lit`)
       variable_instance (:obj:`Variable`)
       boolean (:obj:`Bool`): either ``TRUE`` or ``FALSE``.

    Return:
       Lit formed by assigning ``variable_instance`` to ``boolean`` in ``literal``.
    """
    if literal.value == variable_instance:
        return lit(boolean)
    if literal.value == - variable_instance:
        return neg(lit(boolean))
    return literal


def assign_variable_in_clause(
    clause_instance: Clause, variable_instance: Variable, boolean: Bool
) -> Clause:
    """Assign Bool value to a Variable if present in Clause.

    Replace all instances of ``variable_instance`` and its negation in ``clause_instance`` with
    ``boolean`` and its negation respectively. Leave all else unchanged. Perform tautological
    reductions on the Clause before returning results. This function is idempotent.

    Args:
       clause_instance (:obj:`set[Lit]`): an abstract set (set or frozenset) of Lits.
       variable_instance (:obj:`Variable`)
       boolean (:obj:`Bool`): either ``TRUE`` or ``FALSE``.

    Return:
       Tautologically-reduced Clause formed by assigning ``variable_instance`` to ``boolean``
          in ``clause_instance``.
    """
    assign_variable: Callable[[Lit], Lit]
    assign_variable = ft.partial(
        assign_variable_in_lit, variable_instance=variable_instance, boolean=boolean
    )
    mapped_lits: set[Lit]
    mapped_lits = set(map(assign_variable, clause_instance))

    return tautologically_reduce_clause(clause(mapped_lits))


def assign_variable_in_cnf(
    cnf_instance: Cnf, variable_instance: Variable, boolean: Bool
) -> Cnf:
    """Assign Bool value to a Variable if present in Cnf.

    Replace all instances of ``variable_instance`` and its negation in ``cnf_instance`` with
    ``boolean`` and its negation respectively. Leave all else unchanged. Perform tautological
    reductions on the Cnf before returning results. This function is idempotent.

    Args:
       cnf_instance (:obj:`set[set[Lit]]`): an abstract set (set or frozenset) of abstract sets
          of Lits.
       variable_instance (:obj:`Variable`)
       boolean (:obj:`Bool`): either ``TRUE`` or ``FALSE``.

    Return:
       Tautologically-reduced Cnf formed by assigning ``variable_instance`` to ``boolean`` in
          ``cnf_instance``.
    """
    assign_variable: Callable[[Clause], Clause]
    assign_variable = ft.partial(
        assign_variable_in_clause, variable_instance=variable_instance, boolean=boolean
    )

    mapped_clauses: set[Clause]
    mapped_clauses = set(map(assign_variable, cnf_instance))

    return tautologically_reduce_cnf(cnf(mapped_clauses))


def assign(cnf_instance: Cnf, assignment: Assignment) -> Cnf:
    """Assign Bool values to Variables if present in Cnf.

    For each Variable (key) in ``assignment``, replace the Variable and its negation in
    ``cnf_instance`` using the Bool (value) in ``assignment``. The final output is always
    tautologically reduced. This function is idempotent.

    Args:
       cnf_instance (:obj:`Cnf`)
       assignment (:obj:`Assignment`): a dict with keys being Variables to be replaced and
          values being Bools that the Variables are to be assigned to.  The ``assignment``
          dict need not be complete and can be partial.

    Edge case:
       An empty assignment dict results in ``cnf_instance`` simply getting tautologically
          reduced.

    Return:
       Tautologically-reduced Cnf formed by replacing every key in the ``assignment`` dict (and
          those keys' negations) by corresponding Bool values.
    """
    for variable_instance, boolean in assignment.items():
        cnf_instance = assign_variable_in_cnf(cnf_instance, variable_instance, boolean)
    return tautologically_reduce_cnf(cnf_instance)


def int_repr(cnf_instance: Cnf) -> tuple[tuple[int | Bool, ...], ...]:
    return tuple(tuple(literal.value for literal in clause_instance) for clause_instance in cnf_instance)

if __name__ == "__main__":  # pragma: no cover
    logger.info("Literals can be constructed using the lit function")
    logger.info(f"{lit(3) = }")
    logger.info("Cnfs can be constructed using the cnf() function.")
    logger.info(f"{cnf([[1, -2], [3, 500]]) = }")

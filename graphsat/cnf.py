#!/usr/bin/env python3.8
"""Constructors and functions for sentences in conjunctive normal form (Cnf)."""

# Imports
# =======
import functools as ft
from collections.abc import Callable, Iterator
from typing import Collection, Final, FrozenSet, Mapping, NewType, Set, Union

from loguru import logger

# Classes and Types
# =================
Variable = NewType("Variable", int)
Variable.__doc__ = """`Variable` is a subtype of `int`."""


class Lit(int):
    """`Lit` is a subclass of `int`. It has no other special methods."""


class Bool(Lit):
    """`Bool` is a subclass of `Lit`.

    It overrides the ``__str__``, ``__repr__``, ``__hash__`` and ``__eq__``
    methods inherited from :obj:`int` (and from Lit).
    """

    def __str__(self) -> str:
        """Bool(0) and Bool(1) are treated as constant values labeled FALSE and TRUE."""
        if self.__int__() == 0:
            return "<Bool: FALSE>"
        if self.__int__() == 1:
            return "<Bool: TRUE>"
        raise ValueError("In-valid Bool value encountered.")

    __repr__ = __str__

    def __hash__(self) -> int:
        """Ensure that ``hash(Bool(n))`` doesn't clash with ``hash(n)``."""
        return hash(str(self))

    def __eq__(self, other: object) -> bool:
        """Make ``Bool(n)`` unequal to ``n``."""
        return hash(self) == hash(other)


#: ``TRUE = Bool(1)``, a final instance of Bool.
TRUE: Final = Bool(1)
#: ``FALSE = Bool(0)``, a final instance of Bool.
FALSE: Final = Bool(0)  # Instances of Bool, needed to define Clause and Cnf


class Clause(FrozenSet[Lit]):  # pylint: disable=too-few-public-methods
    """`Clause` is a subclass of `frozenset[Lit]`."""

    def __str__(self) -> str:
        """Pretty print a Clause after sorting its contents."""
        sorted_clause: list[Lit] = sorted(self, key=absolute_value)
        return "(" + ",".join(map(str, sorted_clause)) + ")"


class Cnf(FrozenSet[Clause]):  # pylint: disable=too-few-public-methods
    """`Cnf` is a subclass of `frozenset[Clause]`."""

    def __str__(self) -> str:
        """Pretty print a Cnf after sorting its sorted clause tuples."""
        sorted_cnf: list[Clause]
        sorted_cnf = sorted(self, key=lambda clause_: sum(lit < 0 for lit in clause_))
        sorted_cnf = sorted(sorted_cnf, key=len)

        cnf_tuple: Iterator[str] = map(str, map(clause, sorted_cnf))
        return "".join(cnf_tuple)


Assignment = Mapping[Variable, Bool]  # defines a type alias

# Constructor Functions
# =====================
def variable(positive_int: int) -> Variable:
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


@ft.singledispatch
def lit(int_or_bool: Union[int, Bool]) -> Lit:
    """Constructor-function for Lit type.

    By definition, a `Lit` is in the set ℤ ∪ {`TRUE`, `FALSE`} ∖ {0}`.
    This function is idempotent.
    """
    raise TypeError("Lit must be either Bool or int.")


@lit.register
def lit_bool(arg: Bool) -> Lit:
    """Return as is because Bool is already a subtype of Lit."""
    return arg


@lit.register
def lit_int(arg: int) -> Lit:
    """Cast to Lit."""
    if arg != 0:
        return Lit(arg)
    raise ValueError("Lit must be a nonzero integer.")


def clause(lit_collection: Collection[int]) -> Clause:
    """Constructor-function for Clause type.

    By definition, a `Clause` is a nonempty frozenset of Lits. This function is idempotent.

    Args:
       lit_collection (:obj:`Collection[int]`): a nonempty collection of ints.

    Return:
       Check that each element in the collection satisfies axioms for being a Lit and then cast to
          Clause.

    Raises:
       ValueError: if ``lit_collection`` is an empty collection.

    """
    if not lit_collection:
        raise ValueError(f"Encountered empty input {list(lit_collection)}.")
    return Clause(frozenset(map(lit, lit_collection)))


def cnf(clause_collection: Collection[Collection[int]]) -> Cnf:
    """Constructor-function for Cnf type.

    By definition, a `Cnf` is a nonempty frozenset of Clauses. This function is idempotent.

    Args:
       clause_collection (:obj:`Collection[Collection[int]]`): a nonempty collection (list, tuple,
          set, frozenset) of nonempty collections of integers or Bools.

    Return:
       Check that each element in the collection satisfies axioms for being a Clause and then cast to
          Cnf.

    Raises:
       ValueError: if ``clause_collection`` is an empty collection.
    """
    if not clause_collection:
        raise ValueError(f"Encountered empty input {list(clause_collection)}.")
    return Cnf(frozenset(map(clause, clause_collection)))


# Helpful Constants
# =================
_TRUE_CLAUSE: Final[Clause] = clause([TRUE])
_FALSE_CLAUSE: Final[Clause] = clause([FALSE])
_TRUE_CNF: Final[Cnf] = cnf([_TRUE_CLAUSE])
_FALSE_CNF: Final[Cnf] = cnf([_FALSE_CLAUSE])  # not documented, for internal use only

# Basic Functions
# ===============
def neg(literal: Lit) -> Lit:
    """Negate a Lit.

    This function is an involution.

    Args:
       literal (:obj:`Lit`): a Lit formed from a nonzero integer or from a Bool.

    Return:
       Return the Lit cast from the negative of ``literal``. If ``literal`` is of type Bool, then
          return ``TRUE`` for ``FALSE``, ``FALSE`` for ``TRUE``.

    """
    if literal == TRUE:
        return FALSE
    if literal == FALSE:
        return TRUE
    return lit(-literal)


def absolute_value(literal: Lit) -> Lit:
    """Unnegated form of a Lit.

    This function is idempotent.

    Args:
       literal (:obj:`Lit`): a Lit formed from a nonzero integer.

    Return:
       Check that ``literal`` is not of type Bool and then return the absolute value of ``literal``.
          If it is of type Bool, then return ``literal`` as is.
    """
    if isinstance(literal, Bool):
        return literal
    return lit(abs(literal))


def lits(cnf_instance: Cnf) -> FrozenSet[Lit]:
    """Return frozenset of all Lits that appear in a Cnf.

    Args:
       cnf_instance (:obj:`Cnf`)

    Return:
       A frozenset of all lits that appear in a Cnf.
    """
    return frozenset.union(*cnf_instance)


# Functions for Simplification
# ============================
def tautologically_reduce_clause(lit_set: Set[Lit]) -> Clause:
    r"""Reduce a Clause using various tautologies.

    The order in which these reductions are performed is important. This function is idempotent.

    Tautologies affecting Clauses:
       (⊤ ∨ c = ⊤)  (⊥ = ⊥)  (⊥ ∨ c = c)  (c ∨ ¬c = ⊤),
       where `x` is a Clause, `⊤` represents ``TRUE``, `⊥` represents ``FALSE``, and `∨` is
          disjunction.

    Args:
       lit_set (:obj:`Set[Lit]`): an abstract set (a set or a frozenset) of Lits.

    Return:
       The Clause formed by performing all the above-mentioned tautological reductions.
    """
    if TRUE in lit_set:
        return _TRUE_CLAUSE
    if lit_set == {FALSE}:
        return _FALSE_CLAUSE
    if FALSE in lit_set:
        lit_set -= _FALSE_CLAUSE
    if not set(map(neg, lit_set)).isdisjoint(lit_set):
        return _TRUE_CLAUSE
    return clause(lit_set)


def tautologically_reduce_cnf(clause_set: Set[Set[Lit]]) -> Cnf:
    r"""Reduce a Cnf using various tautologies.

    The order in which these reductions are performed is important. This function is idempotent. This
    is a recursive function that is guaranteed to terminate.

    Tautologies affecting Cnfs:
       (x ∧ ⊥ = ⊥)  (⊤ = ⊤)  (⊤ ∧ x = x),
       where `x` is a Cnf, `⊤` represents ``TRUE``, `⊥` represents ``FALSE``, and `∧` is conjunction.

    Args:
       clause_set (:obj:`Set[Set[Lit]]`): an abstract set (set or frozenset) of abstract sets of Lits.

    Return:
       The Cnf formed by first reducing all the clauses tautologically and then performing all the
       above-mentioned tautological reductions on the Cnf itself.
    """
    clause_set_reduced: set[Clause]
    clause_set_reduced = set(map(tautologically_reduce_clause, clause_set))

    if _FALSE_CLAUSE in clause_set_reduced:
        return _FALSE_CNF
    if clause_set_reduced == _TRUE_CNF:
        return _TRUE_CNF
    if _TRUE_CLAUSE in clause_set_reduced:
        return tautologically_reduce_cnf(clause_set_reduced - _TRUE_CNF)
    return cnf(clause_set_reduced)


# Functions for Assignment
# ========================
def assign_variable_in_lit(
    literal: Lit, variable_instance: Variable, boolean: Bool
) -> Lit:
    """Assign Bool value to a Variable if present in Lit.

    Replace all instances of ``variable_instance`` and its negation with ``boolean`` and its negation
    respectively. Leave all else unchanged. This function is idempotent.

    Args:
       literal (:obj:`Lit`)
       variable_instance (:obj:`Variable`)
       boolean (:obj:`Bool`): either ``TRUE`` or ``FALSE``.

    Return:
       Lit formed by assigning ``variable_instance`` to ``boolean`` in ``literal``.
    """
    if literal == variable_instance:
        return boolean
    if neg(literal) == variable_instance:
        return neg(boolean)
    return literal


def assign_variable_in_clause(
    lit_set: Set[Lit], variable_instance: Variable, boolean: Bool
) -> Clause:
    """Assign Bool value to a Variable if present in Clause.

    Replace all instances of ``variable_instance`` and its negation in ``lit_set`` with ``boolean``
    and its negation respectively. Leave all else unchanged. Perform tautological reductions on the
    Clause before returning results. This function is idempotent.

    Args:
       lit_set (:obj:`Set[Lit]`): an abstract set (set or frozenset) of Lits.
       variable_instance (:obj:`Variable`)
       boolean (:obj:`Bool`): either ``TRUE`` or ``FALSE``.

    Return:
       Tautologically-reduced Clause formed by assigning ``variable_instance`` to ``boolean`` in
          ``lit_set``.
    """
    assign_variable: Callable[[Lit], Lit]
    assign_variable = ft.partial(
        assign_variable_in_lit, variable_instance=variable_instance, boolean=boolean
    )
    mapped_lits: set[Lit]
    mapped_lits = set(map(assign_variable, lit_set))

    return tautologically_reduce_clause(mapped_lits)


def assign_variable_in_cnf(
    clause_set: Set[Set[Lit]], variable_instance: Variable, boolean: Bool
) -> Cnf:
    """Assign Bool value to a Variable if present in Cnf.

    Replace all instances of ``variable_instance`` and its negation in ``clause_set`` with
    ``boolean`` and its negation respectively. Leave all else unchanged. Perform tautological
    reductions on the Cnf before returning results. This function is idempotent.

    Args:
       clause_set (:obj:`Set[Set[Lit]]`): an abstract set (set or frozenset) of abstract sets of
          Lits.
       variable_instance (:obj:`Variable`)
       boolean (:obj:`Bool`): either ``TRUE`` or ``FALSE``.

    Return:
       Tautologically-reduced Cnf formed by assigning ``variable_instance`` to ``boolean`` in
          ``clause_set``.
    """
    assign_variable: Callable[[Clause], Clause]
    assign_variable = ft.partial(
        assign_variable_in_clause, variable_instance=variable_instance, boolean=boolean
    )

    mapped_clauses: set[Clause]
    mapped_clauses = set(map(assign_variable, clause_set))

    return tautologically_reduce_cnf(mapped_clauses)


def assign(cnf_instance: Cnf, assignment: Assignment) -> Cnf:
    """Assign Bool values to Variables if present in Cnf.

    For each Variable (key) in ``assignment``, replace the Variable and its negation in
    ``cnf_instance`` using the Bool (value) in ``assignment``. The final output is always
    tautologically reduced. This function is idempotent.

    Args:
       cnf_instance (:obj:`Cnf`)
       assignment (:obj:`Assignment`): a dict with keys being Variables to be replaced and values
          being Bools that the Variables are to be assigned to.  The ``assignment`` dict need not be
          complete and can be partial.

    Edge case:
       An empty assignment dict results in ``cnf_instance`` simply getting topologically reduced.

    Return:
       Tautologically-reduced Cnf formed by replacing every key in the ``assignment`` dict (and those
          keys' negations) by corresponding Bool values.
    """
    cnf_copy: frozenset[Clause] = cnf_instance.copy()
    for variable_instance, boolean in assignment.items():
        cnf_copy = assign_variable_in_cnf(cnf_copy, variable_instance, boolean)
    return tautologically_reduce_cnf(cnf_copy)


if __name__ == "__main__":
    logger.info("Cnfs can be constructed using the cnf() function.")
    logger.info(">>> cnf([[1, -2], [3, 500]])")
    logger.info(cnf([[1, -2], [3, 500]]))

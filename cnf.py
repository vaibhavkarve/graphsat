#!/usr/bin/env python3
"""Constructors and methods for sentences in conjunctive normal form (CNF).

Definition of a CNF
===================

   - A Variable is simply a set of symbols that can be assigned the value of True or
     False in a boolean expression.
   - A Lit is either a Variable, the negation of a Variable, or the symbols
     representing True and False.
   - A Clause is a boolean expression made of the disjunction of Lits.
   - A CNF is the boolean expression made of the conjunction of Clauses.
"""
# Imports from standard library.
import functools as ft
from typing import (AbstractSet, Callable, Collection, FrozenSet, Iterator, Final, List,
                    Mapping, NewType, Set, Union)
# Imports from third-party.
from loguru import logger


# Classes and Types
# =================

Variable = NewType('Variable', int)
Variable.__doc__ = """`Variable` is a subtype of `int`."""


class Lit(int):
    """`Lit` is a subclass of `int`. It has no other special methods."""


class Bool(Lit):
    """`Bool` is a subclass of `Lit`.

    It overrides the ``__str__``, ``__repr__``, ``__hash__`` and ``__eq__`` methods
    inherited from :obj:`int` (and from Lit).
    """

    def __str__(self) -> str:
        """Bool(0) and Bool(1) are treated as constant values labeled FALSE and TRUE."""
        if self.__int__() == 0:
            return '<Bool: FALSE>'
        if self.__int__() == 1:
            return '<Bool: TRUE>'
        raise ValueError('In-valid Bool value encountered.')

    __repr__ = __str__

    def __hash__(self) -> int:
        """Ensure that ``hash(Bool(n))`` doesn't clash with ``hash(n)``."""
        return hash(str(self))

    def __eq__(self, other: object) -> bool:
        """Make ``Bool(n)`` unequal to ``n``."""
        return hash(self) == hash(other)


#: ``TRUE = Bool(1)``, a final instance of Bool.
TRUE: Final[Bool] = Bool(1)

#: ``FALSE = Bool(0)``, a final instance of Bool.
FALSE: Final[Bool] = Bool(0)


class Clause(FrozenSet[Lit]):  # pylint: disable=too-few-public-methods
    """`Clause` is a subclass of `FrozenSet[Lit]`."""

    def __str__(self) -> str:
        """Pretty print a Clause.

        Args:
           self (:obj:`CNF`)
        """
        sorted_clause: List[Lit]
        try:
            sorted_clause = sorted(self, key=absolute_value)
        except ValueError:
            # clause probably contains TRUE/FALSE.
            sorted_clause = self
        return '(' + ','.join(map(str, sorted_clause)) + ')'


class CNF(FrozenSet[Clause]):  # pylint: disable=too-few-public-methods
    """`CNF` is a subclass of `FrozenSet[Clause]`."""

    def __str__(self) -> str:
        """Pretty print a CNF.

        Args:
           self (:obj:`CNF`):

        Return:
           A sorted string of sorted clause tuples.
        """
        sorted_cnf: List[Clause]
        sorted_cnf = sorted(self, key=lambda clause_: sum([lit < 0 for lit in clause_]))
        sorted_cnf = sorted(sorted_cnf, key=len)

        cnf_tuple: Iterator[str] = map(str, map(clause, sorted_cnf))
        return ''.join(cnf_tuple)


# Constructor Functions
# =====================


def variable(positive_int: int) -> Variable:
    """Constructor-function for Variable type.

    By definition, a `Variable` is just a positive integer.
    This function is idempotent.

    Args:
       positive_int (:obj:`int`):

    Return:
       If input is indeed positive, then return ``positive_int`` after casting to
       Variable.

    Raises:
       ValueError: if ``positive_int <= 0``.

    """
    if positive_int <= 0:
        raise ValueError('Variable must be a positive integer.')
    return Variable(positive_int)


@ft.singledispatch
def lit(int_or_Bool: Union[int, Bool]) -> Lit:  # pylint: disable=invalid-name
    r"""Constructor-function for Lit type.

    By definition, a `Lit` is in the set :math:`\mathbb{Z} \cup \{`:obj:`TRUE`,
    :obj:`FALSE` :math:`\} - \{0\}`.
    This function is idempotent.
    """
    raise TypeError('Lit must be either Bool or int.')


@lit.register
def lit_bool(arg: Bool) -> Lit:
    """Return as is because Bool is already a subtype of Lit."""
    return arg


@lit.register
def lit_int(arg: int) -> Lit:
    """Cast to Lit."""
    if arg != 0:
        return Lit(arg)
    raise ValueError('Lit must be a nonzero integer.')



def clause(lit_collection: Collection[int]) -> Clause:
    """Constructor-function for Clause type.

    By definition, a `Clause` is a nonempty frozenset of Lits.
    This function is idempotent.

    Args:
       lit_collection (:obj:`Collection[int]`): a nonempty collection (list, tuple,
          set, frozenset, or iterator of integers or Bools.

    Return:
       Check that each element in the collection satisfies axioms for being a Lit and
       then cast to Clause.

    Raises:
       ValueError: if ``lit_collection`` is an empty collection.

    """
    if not lit_collection:
        raise ValueError(f'Encountered empty input {list(lit_collection)}.')
    return Clause(frozenset(map(lit, lit_collection)))


def cnf(clause_collection: Collection[Collection[int]]) -> CNF:
    """Constructor-function for CNF type.

    By definition, a `CNF` is a nonempty frozenset of Clauses.
    This function is idempotent.

    Args:
       clause_collection (:obj:`Collection[Collection[int]]`): a nonempty collection
       (list, tuple, set, frozenset) of nonempty collections of integers or Bools.

    Return:
       Check that each element in the collection satisfies axioms for being a Clause and
       then cast to CNF.

    Raises:
       ValueError: if ``clause_collection`` is an empty collection.

    """
    if not clause_collection:
        raise ValueError(f'Encountered empty input {list(clause_collection)}.')
    return CNF(frozenset(map(clause, clause_collection)))


# Helpful Constants
# =================
# (not documented, for internal use only)


TRUE_CLAUSE: Final[Clause] = clause([TRUE])
FALSE_CLAUSE: Final[Clause] = clause([FALSE])
TRUE_CNF: Final[CNF] = cnf([[TRUE]])
FALSE_CNF: Final[CNF] = cnf([[FALSE]])


# Basic Functions
# ===============


def neg(literal: Lit) -> Lit:
    """Negate a Lit.

    This function is an involution.

    Args:
       literal (:obj:`Lit`): a Lit formed from a nonzero integer.

    Return:
       Check that ``literal`` is not of type Bool and then return the
       Lit cast from the negative of `literal`.

    Raises:
       ValueError: if ``literal`` is ``TRUE`` or ``FALSE``.

    """
    if isinstance(literal, Bool):
        raise ValueError('Negation of TRUE/FALSE is not defined.')
    return lit(-literal)


def absolute_value(literal: Lit) -> Lit:
    """Unnegated form of a Lit.

    This function is idempotent.

    Args:
       literal (:obj:`Lit`): a Lit formed from a nonzero integer.

    Return:
       Check that ``literal`` is not of type Bool and then return the absolute
       value of ``literal``.

    Raises:
       ValueError: If `literal` is :obj:`Bool.TRUE` or :obj:`Bool.FALSE`.

    """
    if isinstance(literal, Bool):
        raise ValueError(f'Absolute value not defined for {literal}.')
    return lit(abs(literal))


def lits(cnf_instance: CNF) -> FrozenSet[Lit]:
    """Return frozenset of all Lits that appear in a CNF.

    Args:
       cnf_instance (:obj:`CNF`)

    Return:
       A frozenset of all lits that appear in a CNF.

    """
    return frozenset.union(*cnf_instance)



# Functions for Simplification
# ============================


def tautologically_reduce_clause(lit_set: AbstractSet[Lit]) -> Clause:
    r"""Reduce a Clause using various tautologies.

    The order in which these reductions are performed is important.
    This function is idempotent.

    Tautologies affecting Clauses:
       .. math::
          ⊤ \vee c = ⊤, \quad ⊥ = ⊥, \quad ⊥ \vee c = c, \quad c \vee -c = ⊤.

       where :math:`x` is a Clause, ⊤ represents ``TRUE``, ⊥ represents ``FALSE``, and
       :math:`\vee` is disjunction.

    Args:
       lit_set (:obj:`AbstractSet[Lit]`): an abstract set (a set or a frozenset)
          of Lits.

    Return:
       The Clause formed by performing all the above-mentioned tautological reductions.

    """
    if TRUE in lit_set:
        return TRUE_CLAUSE
    if lit_set == {FALSE}:
        return FALSE_CLAUSE
    if FALSE in lit_set:
        lit_set -= FALSE_CLAUSE
    if not set(map(neg, lit_set)).isdisjoint(lit_set):
        return TRUE_CLAUSE
    return clause(lit_set)


def tautologically_reduce_cnf(clause_set: AbstractSet[AbstractSet[Lit]]) -> CNF:
    r"""Reduce a CNF using various tautologies.

    The order in which these reductions are performed is important.
    This function is idempotent.

    Tautologies affecting CNFs:
       .. math::
          x~ \wedge ⊥ = ⊥, \quad ⊤ = ⊤, \quad ⊤ \wedge x = x.

       where :math:`x` is a CNF, ⊤ represents ``TRUE``, ⊥ represents ``FALSE``, and
       :math:`\wedge` is conjunction.

    Args:
       clause_set (:obj:`AbstractSet[AbstractSet[Lit]]`): an abstract set (a set or
          frozenset) of abstract sets of Lits.

    Return:
       The CNF formed by first reducing all the clauses tautologically and then performing
       all the above-mentioned tautological reductions on the CNF itself.

    """
    clause_set_reduced: Set[Clause]
    clause_set_reduced = set(map(tautologically_reduce_clause, clause_set))

    if FALSE_CLAUSE in clause_set_reduced:
        return FALSE_CNF
    if clause_set_reduced == TRUE_CNF:
        return TRUE_CNF
    if TRUE_CLAUSE in clause_set_reduced:
        return tautologically_reduce_cnf(clause_set_reduced - TRUE_CNF)
    return cnf(clause_set_reduced)


# Functions for Assignment
# ========================

def assign_variable_in_lit(literal: Lit,
                           variable_instance: Variable,
                           boolean: Bool) -> Lit:
    """Assign Bool value to a Variable if present in Lit.

    Replace all instances of ``variable_instance`` and its negation with ``boolean``
    and its negation respectively.
    Leave all else unchanged.
    This function is idempotent.

    Args:
       literal (:obj:`Lit`)
       variable_instance (:obj:`Variable`)
       boolean (:obj:`Bool`): either ``TRUE`` or ``FALSE``.

    Return:
       Lit formed by assigning ``variable_instance`` to ``boolean`` in
       ``literal``.

    """
    if isinstance(literal, Bool):
        return literal
    if literal == variable_instance:
        return boolean
    if neg(literal) == variable_instance:
        return FALSE if boolean == TRUE else TRUE
    return literal


def assign_variable_in_clause(lit_set: AbstractSet[Lit],
                              variable_instance: Variable,
                              boolean: Bool) -> Clause:
    """Assign Bool value to a Variable if present in Clause.

    Replace all instances of ``variable_instance`` and its negation in ``lit_set``
    with ``boolean`` and its negation respectively.
    Leave all else unchanged.
    Perform tautological reductions on the Clause before returning results.
    This function is idempotent.

    Args:
       lit_set (:obj:`AbstractSet[Lit]`): an abstract set (set or frozenset) of
          Lits.
       variable_instance (:obj:`Variable`)
       boolean (:obj:`Bool`): either ``TRUE`` or ``FALSE``.

    Return:
       Tautologically-reduced Clause formed by assigning ``variable_instance`` to
       ``boolean`` in ``lit_set``.

    """
    assign_variable: Callable[[Lit], Lit]
    assign_variable = ft.partial(assign_variable_in_lit,
                                 variable_instance=variable_instance,
                                 boolean=boolean)
    mapped_lits: Set[Lit]
    mapped_lits = set(map(assign_variable, lit_set))

    return tautologically_reduce_clause(mapped_lits)


def assign_variable_in_cnf(clause_set: AbstractSet[AbstractSet[Lit]],
                           variable_instance: Variable,
                           boolean: Bool) -> CNF:
    """Assign Bool value to a Variable if present in CNF.

    Replace all instances of ``variable_instance`` and its negation in ``clause_set``
    with ``boolean`` and its negation respectively.
    Leave all else unchanged.
    Perform tautological reductions on the CNF before returning results.
    This function is idempotent.

    Args:
       clause_set (:obj:`AbstractSet[AbstractSet[Lit]]`): an abstract set (set or
          frozenset) of abstract sets of Lits.
       variable_instance (:obj:`Variable`)
       boolean (:obj:`Bool`): either ``TRUE`` or ``FALSE``.

    Return:
       Tautologically-reduced CNF formed by assigning ``variable_instance`` to
       ``boolean`` in ``clause_set``.

    """
    assign_variable: Callable[[Clause], Clause]
    assign_variable = ft.partial(assign_variable_in_clause,
                                 variable_instance=variable_instance,
                                 boolean=boolean)

    mapped_clauses: Set[Clause]
    mapped_clauses = set(map(assign_variable, clause_set))

    return tautologically_reduce_cnf(mapped_clauses)


def assign(cnf_instance: CNF, assignment: Mapping[Variable, Bool]) -> CNF:
    """Assign Bool values to Variables if present in CNF.

    For each Variable (key) in ``assignment``, replace the Variable and its negation in
    ``cnf_instance`` using the Bool (value) in ``assignment``.
    The final output is always tautologically reduced.
    This function is idempotent.

    Args:
       cnf_instance (:obj:`CNF`)
       assignment (:obj:`Mapping[Variable, Bool]`): a dictionary with keys being Variables
          to be replaced and values being Bools that the Variables are to be assigned to.
          The ``assignment`` dictionary need not be complete and can be partial.

    Edge case:
       An empty assignment dictionary results in ``cnf_instance`` simply getting
       topologically reduced.

    Return:
       Tautologically-reduced CNF formed by replacing every key in the ``assignment``
       dictionary (and those keys' negations) by corresponding Bool values.

    """
    cnf_copy: FrozenSet[Clause] = cnf_instance.copy()
    for variable_instance, boolean in assignment.items():
        cnf_copy = assign_variable_in_cnf(cnf_copy, variable_instance, boolean)
    return tautologically_reduce_cnf(cnf_copy)


if __name__ == '__main__':
    logger.info('CNFs can be constructed using the cnf() function.')
    logger.info('>>> cnf([[1, -2], [3, 500]])')
    logger.info(cnf([[1, -2], [3, 500]]))

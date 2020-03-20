#!/usr/bin/env python3
"""Constructors and methods for sentences in conjunctive normal form (CNF).

Definition of a CNF
===================

   - A Variable is simply a set of symbols that can be assigned the value of True or
     False in a boolean expression.
   - A Literal is either a Variable, the negation of a Variable, or the symbols
     representing True and False.
   - A Clause is a boolean expression made of the disjunction of Literals.
   - A CNF is the boolean expression made of the conjunction of Clauses.
"""
import functools as ft
from typing import (AbstractSet, Callable, FrozenSet, Iterable, Iterator, List, Mapping,
                    NewType, Set, Union)
from loguru import logger  # type: ignore[import]


# Classes and Types
# =================


class Literal(int):
    """`Literal` is a subclass of `int`. It has no other special methods."""


class Bool(Literal):
    """`Bool` is a subclass of `Literal`.

    It overrides the ``__str__``, ``__repr__``, ``__hash__`` and ``__eq__`` methods
    inherited from :obj:`int` (and from Literal).
    """

    def __str__(self) -> str:
        """Bool(0) and Bool(1) are treated as constant values labeled FALSE and TRUE."""
        if self.__int__() == 0:
            return f'<Bool: FALSE>'
        if self.__int__() == 1:
            return f'<Bool: TRUE>'
        return f'<Bool: {self.__int__()}>'

    __repr__ = __str__

    def __hash__(self) -> int:
        """Ensure that ``hash(Bool(n))`` doesn't clash with ``hash(n)``."""
        return hash(str(self))

    def __eq__(self, other: object) -> bool:
        """Make ``Bool(n)`` unequal to ``n``."""
        return hash(self) == hash(other)


#: ``TRUE = Bool(1)``, a final instance of Bool.
TRUE: Bool = Bool(1)

#: ``FALSE = Bool(0)``, a final instance of Bool.
FALSE: Bool = Bool(0)

Variable = NewType('Variable', int)
Variable.__doc__ = """`Variable` is a subtype of `int`."""

Clause = NewType('Clause', FrozenSet[Literal])
Clause.__doc__ = """`Clause` is a subtype of `FrozenSet[Literal]`."""

CNF = NewType('CNF', FrozenSet[Clause])
CNF.__doc__ = """`CNF` is a subtype of `FrozenSet[Clause]`."""

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


def literal(int_or_Bool: Union[int, Bool]) -> Literal:  # pylint: disable=invalid-name
    r"""Constructor-function for Literal type.

    By definition, a `Literal` is in the set :math:`\mathbb{Z} \cup \{`:obj:`TRUE`,
    :obj:`FALSE` :math:`\} - \{0\}`.
    This function is idempotent.

    Args:
       int_or_Bool (:obj:`int` or :obj:`Bool`): either a nonzero integer, or ``TRUE``, or
          ``FALSE``.

    Return:
       - if input is ``TRUE`` or ``FALSE``, then return input as is (since Bool is already
         a subtype of Literal.)
       - if input is a nonzero integer, then return ``int_or_Bool`` after casting to
         Literal.

    Raises:
       ValueError: if ``int_or_Bool == 0``.

    """
    if isinstance(int_or_Bool, Bool):
        # int_or_Bool is TRUE/FALSE.
        return int_or_Bool
    if int_or_Bool != 0:
        return Literal(int_or_Bool)
    raise ValueError('Literal must be either TRUE/FALSE or a nonzero integer.')


def clause(literal_iterable: Iterable[int]) -> Clause:
    """Constructor-function for Clause type.

    By definition, a `Clause` is a nonempty frozenset of Literals.
    This function is idempotent.

    Args:
       literal_iterable (:obj:`Iterable[int]`): a nonempty iterable (list, tuple,
          set, frozenset, or iterator of integers or Bools.

    Return:
       Check that each element in the iterable satisfies axioms for being a Literal and
       then cast to Clause.

    Raises:
       ValueError: if ``literal_iterable`` is an empty iterable.

    """
    if not literal_iterable:
        raise ValueError(f'Encountered empty input {list(literal_iterable)}.')
    return Clause(frozenset(map(literal, literal_iterable)))


def cnf(clause_iterable: Iterable[Iterable[int]]) -> CNF:
    """Constructor-function for CNF type.

    By definition, a `CNF` is a nonempty frozenset of Clauses.
    This function is idempotent.

    Args:
       clause_iterable (:obj:`Iterable[Iterable[int]]`): a nonempty iterable (list,
       tuple, set, frozenset, or iterator) of nonempty iterables of integers or Bools.

    Return:
       Check that each element in the iterable satisfies axioms for being a Clause and
       then cast to CNF.

    Raises:
       ValueError: if ``clause_iterable`` is an empty iterable.

    """
    if not clause_iterable:
        raise ValueError(f'Encountered empty input {list(clause_iterable)}.')
    return CNF(frozenset(map(clause, clause_iterable)))


# Helpful Constants
# =================
# (not documented, for internal use only)


TRUE_CLAUSE: Clause = clause([TRUE])
FALSE_CLAUSE: Clause = clause([FALSE])
TRUE_CNF: CNF = cnf([[TRUE]])
FALSE_CNF: CNF = cnf([[FALSE]])


# Basic Functions
# ===============


def neg(literal_instance: Literal) -> Literal:
    """Negate a Literal.

    This function is an involution.

    Args:
       literal_instance (:obj:`Literal`): a Literal formed from a nonzero integer.

    Return:
       Check that ``literal_instance`` is not of type Bool and then return the Literal cast
       from the negative of `literal_instance`.

    Raises:
       ValueError: if ``literal_instance`` is ``TRUE`` or ``FALSE``.

    """
    if isinstance(literal_instance, Bool):
        raise ValueError('Negation of TRUE/FALSE is not defined.')
    return literal(-literal_instance)


def absolute_value(literal_instance: Literal) -> Literal:
    """Unnegated form of a Literal.

    This function is idempotent.

    Args:
       literal_instance (:obj:`Literal`): a Literal formed from a nonzero integer.

    Return:
       Check that ``literal_instance`` is not of type Bool and then return the absolute
       value of ``literal_instance``.

    Raises:
       ValueError: If `literal_instance` is :obj:`Bool.TRUE` or :obj:`Bool.FALSE`.

    """
    if isinstance(literal_instance, Bool):
        raise ValueError('Absolute value not defined for TRUE/FALSE.')
    return literal(abs(literal_instance))


def literals_in_cnf(cnf_instance: CNF) -> FrozenSet[Literal]:
    """Return frozenset of all Literals that appear in a CNF.

    Args:
       cnf_instance (:obj:`CNF`)

    Return:
       A frozenset of all literals that appear in a CNF.

    """
    return frozenset.union(*cnf_instance)


def pprint_cnf(cnf_instance: CNF) -> str:
    """Pretty print a CNF.

    Args:
        cnf_instance (:obj:`CNF`)

    Return:
        A sorted string of sorted clause tuples.

    """
    sorted_clauses: Iterator[List[Literal]]
    sorted_clauses = map(lambda clause_: sorted(clause_, key=absolute_value), cnf_instance)

    sorted_cnf: List[List[Literal]]
    sorted_cnf = sorted(sorted_clauses, key=lambda clause_:
                        sum([literal_ < 0 for literal_ in clause_]))
    sorted_cnf = sorted(sorted_cnf, key=len)

    def pprint_clause(clause_: List[Literal]) -> str:
        return '(' + ','.join(map(str, clause_)) + ')'

    return ''.join(map(pprint_clause, sorted_cnf))


# Functions for Simplification
# ============================


def tautologically_reduce_clause(literal_set: AbstractSet[Literal]) -> Clause:
    r"""Reduce a Clause using various tautologies.

    The order in which these reductions are performed is important.
    This function is idempotent.

    Tautologies affecting Clauses:
       .. math::
          ⊤ \vee c = ⊤, \quad ⊥ = ⊥, \quad ⊥ \vee c = c, \quad c \vee -c = ⊤.

       where :math:`x` is a Clause, ⊤ represents ``TRUE``, ⊥ represents ``FALSE``, and
       :math:`\vee` is disjunction.

    Args:
       literal_set (:obj:`AbstractSet[Literal]`): an abstract set (a set or a frozenset)
          of Literals.

    Return:
       The Clause formed by performing all the above-mentioned tautological reductions.

    """
    if TRUE in literal_set:
        return TRUE_CLAUSE
    if literal_set == {FALSE}:
        return FALSE_CLAUSE
    if FALSE in literal_set:
        literal_set -= FALSE_CLAUSE
    if not set(map(neg, literal_set)).isdisjoint(literal_set):
        return TRUE_CLAUSE
    return clause(literal_set)


def tautologically_reduce_cnf(clause_set: AbstractSet[AbstractSet[Literal]]) -> CNF:
    r"""Reduce a CNF using various tautologies.

    The order in which these reductions are performed is important.
    This function is idempotent.

    Tautologies affecting CNFs:
       .. math::
          x~ \wedge ⊥ = ⊥, \quad ⊤ = ⊤, \quad ⊤ \wedge x = x.

       where :math:`x` is a CNF, ⊤ represents ``TRUE``, ⊥ represents ``FALSE``, and
       :math:`\wedge` is conjunction.

    Args:
       clause_set (:obj:`AbstractSet[AbstractSet[Literal]]`): an abstract set (a set or
          frozenset) of abstract sets of Literals.

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


def assign_variable_in_literal(literal_instance: Literal,  # pylint: disable=invalid-name
                               variable_instance: Variable,
                               Boolean: Bool) -> Literal:
    """Assign Bool value to a Variable if present in Literal.

    Replace all instances of ``variable_instance`` and its negation with ``Boolean``
    and its negation respectively.
    Leave all else unchanged.
    This function is idempotent.

    Args:
       literal_instance (:obj:`Literal`)
       variable_instance (:obj:`Variable`)
       Boolean (:obj:`Bool`): either ``TRUE`` or ``FALSE``.

    Return:
       Literal formed by assigning ``variable_instance`` to ``Boolean`` in
       ``literal_instance``.

    """
    if isinstance(literal_instance, Bool):
        return literal_instance
    if literal_instance == variable_instance:
        return Boolean
    if neg(literal_instance) == variable_instance:
        return FALSE if Boolean == TRUE else TRUE
    return literal_instance


def assign_variable_in_clause(literal_set: AbstractSet[Literal],  # noqa, pylint: disable=invalid-name
                              variable_instance: Variable,
                              Boolean: Bool) -> Clause:
    """Assign Bool value to a Variable if present in Clause.

    Replace all instances of ``variable_instance`` and its negation in ``literal_set``
    with ``Boolean`` and its negation respectively.
    Leave all else unchanged.
    Perform tautological reductions on the Clause before returning results.
    This function is idempotent.

    Args:
       literal_set (:obj:`AbstractSet[Literal]`): an abstract set (set or frozenset) of
          Literals.
       variable_instance (:obj:`Variable`)
       Boolean (:obj:`Bool`): either ``TRUE`` or ``FALSE``.

    Return:
       Tautologically-reduced Clause formed by assigning ``variable_instance`` to
       ``Boolean`` in ``literal_set``.

    """
    assign_variable: Callable[[Literal], Literal]
    assign_variable = ft.partial(assign_variable_in_literal,
                                 variable_instance=variable_instance,
                                 Boolean=Boolean)
    mapped_literals: Set[Literal]
    mapped_literals = set(map(assign_variable, literal_set))

    return tautologically_reduce_clause(mapped_literals)


def assign_variable_in_cnf(clause_set: AbstractSet[AbstractSet[Literal]],  # noqa, pylint: disable=invalid-name
                           variable_instance: Variable,
                           Boolean: Bool) -> CNF:
    """Assign Bool value to a Variable if present in CNF.

    Replace all instances of ``variable_instance`` and its negation in ``clause_set``
    with ``Boolean`` and its negation respectively.
    Leave all else unchanged.
    Perform tautological reductions on the CNF before returning results.
    This function is idempotent.

    Args:
       clause_set (:obj:`AbstractSet[AbstractSet[Literal]]`): an abstract set (set or
          frozenset) of abstract sets of Literals.
       variable_instance (:obj:`Variable`)
       Boolean (:obj:`Bool`): either ``TRUE`` or ``FALSE``.

    Return:
       Tautologically-reduced CNF formed by assigning ``variable_instance`` to
       ``Boolean`` in ``clause_set``.

    """
    assign_variable: Callable[[Clause], Clause]
    assign_variable = ft.partial(assign_variable_in_clause,
                                 variable_instance=variable_instance,
                                 Boolean=Boolean)

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

    Return:
       Tautologically-reduced CNF formed by replacing every key in the ``assignment``
       dictionary (and those keys' negations) by corresponding Bool values.

    """
    cnf_copy: FrozenSet[Clause] = cnf_instance.copy()
    for variable_instance, Boolean in assignment.items():  # pylint: disable=invalid-name
        cnf_copy = assign_variable_in_cnf(cnf_copy, variable_instance, Boolean)
    return tautologically_reduce_cnf(cnf_copy)


if __name__ == '__main__':
    logger.info(f'Running {__file__} as a stand-alone script.')
    logger.info('CNFs can be constructed using the cnf() function.')
    logger.info('>>> cnf([[1, -2], [3, 500]])')
    logger.info(cnf([[1, -2], [3, 500]]))

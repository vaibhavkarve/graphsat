#!/usr/bin/env python3.9
"""Functions for propositional calculus -- conjunction, disjunction and negation."""

import functools as ft
from loguru import logger

from graphsat.cnf import cnf, Cnf, clause, Clause, Lit, neg, tautologically_reduce_cnf


# Conjunction
# ===========


def literal_and_literal(literal1: Lit, literal2: Lit) -> Cnf:
    return cnf([[literal1], [literal2]])


def clause_and_literal(clause_: Clause, literal: Lit) -> Cnf:
    return cnf([clause_, [literal]])


def clause_and_clause(clause1: Clause, clause2: Clause) -> Cnf:
    return cnf([clause1, clause2])


def cnf_and_literal(cnf1: Cnf, literal: Lit) -> Cnf:
    return cnf(cnf1 | {(literal, )})


def cnf_and_clause(cnf1: Cnf, clause_: Clause) -> Cnf:
    return cnf(cnf1 | {clause_})


def cnf_and_cnf(cnf1: Cnf, cnf2: Cnf) -> Cnf:
    return cnf(cnf1 | cnf2)


# Disjunction
# ===========


def literal_or_literal(literal1: Lit, literal2: Lit) -> Clause:
    return clause([literal1, literal2])


def clause_or_literal(clause_: Clause, literal: Lit) -> Clause:
    return clause(clause_ | {literal})


def clause_or_clause(clause1: Clause, clause2: Clause) -> Clause:
    return clause(clause1 | clause2)


def cnf_or_literal(cnf1: Cnf, literal: Lit) -> Cnf:
    return cnf([clause_or_literal(clause, literal) for clause in cnf1])


def cnf_or_clause(cnf1: Cnf, clause_: Clause) -> Cnf:
    return cnf([clause_or_clause(clause1, clause_) for clause1 in cnf1])


def cnf_or_cnf(cnf1: Cnf, cnf2: Cnf) -> Cnf:
    return ft.reduce(cnf_and_cnf, [cnf_or_clause(cnf1, clause) for clause in cnf2])


# Negation
# ========


def neg_clause(clause1: Clause) -> Cnf:
    return cnf([clause([neg(literal)]) for literal in clause1])


def neg_cnf(cnf1: Cnf) -> Cnf:
    return ft.reduce(cnf_or_cnf, [neg_clause(clause) for clause in cnf1])


if __name__ == '__main__':
    logger.info('Conjunction between two Cnfs:')
    logger.info('>>> cnf_and_cnf(cnf([[1, 2], [3, 4]]), cnf([[-1, 5], [6]]))')
    logger.info(cnf_and_cnf(cnf([[1, 2], [3, 4]]), cnf([[-1, 5], [6]])))
    logger.info('\n')
    logger.info('Disjunction between two Cnfs:')
    logger.info('>>> cnf_or_cnf(cnf([[1, 2], [3, 4]]), cnf([[-1, 5], [6]]))')
    logger.info(cnf_or_cnf(cnf([[1, 2], [3, 4]]), cnf([[-1, 5], [6]])))
    logger.info('>>> tautologically_reduce_cnf(_)')
    logger.info(tautologically_reduce_cnf(cnf_or_cnf(cnf([[1, 2], [3, 4]]),
                                                         cnf([[-1, 5], [6]]))))
    logger.info('\n')
    logger.info('Negation of a Cnf:')
    logger.info('>>> neg_cnf(cnf([[1, -2], [2, -3]]))')
    logger.info(neg_cnf(cnf([[1, -2], [2, -3]])))
    logger.info('>>> tautologically_reduce_cnf(_)')
    logger.info(tautologically_reduce_cnf(neg_cnf(cnf([[1, -2], [2, -3]]))))

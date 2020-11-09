#!/usr/bin/env python3.9
"""Simple functions for propositional calculus.

Currently, this module implements Conjunction, Disjunction and Negation.
"""
import functools as ft
from loguru import logger
from cnf import cnf, CNF, clause, Clause, Lit, neg, tautologically_reduce_cnf


# Conjunction
# ===========


def literal_and_literal(literal1: Lit, literal2: Lit) -> CNF:
    return cnf([[literal1], [literal2]])


def clause_and_literal(clause_: Clause, literal: Lit) -> CNF:
    return cnf([clause_, [literal]])


def clause_and_clause(clause1: Clause, clause2: Clause) -> CNF:
    return cnf([clause1, clause2])


def cnf_and_literal(cnf1: CNF, literal: Lit) -> CNF:
    return cnf(cnf1 | {(literal, )})


def cnf_and_clause(cnf1: CNF, clause_: Clause) -> CNF:
    return cnf(cnf1 | {clause_})


def cnf_and_cnf(cnf1: CNF, cnf2: CNF) -> CNF:
    return cnf(cnf1 | cnf2)


# Disjunction
# ===========


def literal_or_literal(literal1: Lit, literal2: Lit) -> Clause:
    return clause([literal1, literal2])


def clause_or_literal(clause_: Clause, literal: Lit) -> Clause:
    return clause(clause_ | {literal})


def clause_or_clause(clause1: Clause, clause2: Clause) -> Clause:
    return clause(clause1 | clause2)


def cnf_or_literal(cnf1: CNF, literal: Lit) -> CNF:
    return cnf([clause_or_literal(clause, literal) for clause in cnf1])


def cnf_or_clause(cnf1: CNF, clause_: Clause) -> CNF:
    return cnf([clause_or_clause(clause1, clause_) for clause1 in cnf1])


def cnf_or_cnf(cnf1: CNF, cnf2: CNF) -> CNF:
    return ft.reduce(cnf_and_cnf, [cnf_or_clause(cnf1, clause) for clause in cnf2])


# Negation
# ========


def neg_clause(clause1: Clause) -> CNF:
    return cnf([clause([neg(literal)]) for literal in clause1])


def neg_cnf(cnf1: CNF) -> CNF:
    return ft.reduce(cnf_or_cnf, [neg_clause(clause) for clause in cnf1])


if __name__ == '__main__':
    logger.info('Conjunction between two CNFs:')
    logger.info('>>> cnf_and_cnf(cnf([[1, 2], [3, 4]]), cnf([[-1, 5], [6]]))')
    logger.info(cnf_and_cnf(cnf([[1, 2], [3, 4]]), cnf([[-1, 5], [6]])))
    logger.info('\n')
    logger.info('Disjunction between two CNFs:')
    logger.info('>>> cnf_or_cnf(cnf([[1, 2], [3, 4]]), cnf([[-1, 5], [6]]))')
    logger.info(cnf_or_cnf(cnf([[1, 2], [3, 4]]), cnf([[-1, 5], [6]])))
    logger.info('>>> tautologically_reduce_cnf(_)')
    logger.info(tautologically_reduce_cnf(cnf_or_cnf(cnf([[1, 2], [3, 4]]),
                                                         cnf([[-1, 5], [6]]))))
    logger.info('\n')
    logger.info('Negation of a CNF:')
    logger.info('>>> neg_cnf(cnf([[1, -2], [2, -3]]))')
    logger.info(neg_cnf(cnf([[1, -2], [2, -3]])))
    logger.info('>>> tautologically_reduce_cnf(_)')
    logger.info(tautologically_reduce_cnf(neg_cnf(cnf([[1, -2], [2, -3]]))))

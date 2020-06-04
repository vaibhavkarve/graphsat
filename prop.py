#!/usr/bin/env python3
"""Simple functions for propositional calculus.

Currently, this module implements Conjunction, Disjunction and Negation.
"""
import functools as ft
from loguru import logger
import cnf


# Conjunction
# ===========


def literal_and_literal(literal1: cnf.Lit, literal2: cnf.Lit) -> cnf.CNF:
    return cnf.cnf([[literal1], [literal2]])


def clause_and_literal(clause: cnf.Clause, literal: cnf.Lit) -> cnf.CNF:
    return cnf.cnf([clause, [literal]])


def clause_and_clause(clause1: cnf.Clause, clause2: cnf.Clause) -> cnf.CNF:
    return cnf.cnf([clause1, clause2])


def cnf_and_literal(cnf1: cnf.CNF, literal: cnf.Lit) -> cnf.CNF:
    return cnf.cnf(cnf1 | {(literal, )})


def cnf_and_clause(cnf1: cnf.CNF, clause: cnf.Clause) -> cnf.CNF:
    return cnf.cnf(cnf1 | {clause})


def cnf_and_cnf(cnf1: cnf.CNF, cnf2: cnf.CNF) -> cnf.CNF:
    return cnf.cnf(cnf1 | cnf2)


# Disjunction
# ===========


def literal_or_literal(literal1: cnf.Lit, literal2: cnf.Lit) -> cnf.Clause:
    return cnf.clause([literal1, literal2])


def clause_or_literal(clause: cnf.Clause, literal: cnf.Lit) -> cnf.Clause:
    return cnf.clause(clause | {literal})


def clause_or_clause(clause1: cnf.Clause, clause2: cnf.Clause) -> cnf.Clause:
    return cnf.clause(clause1 | clause2)


def cnf_or_literal(cnf1: cnf.CNF, literal: cnf.Lit) -> cnf.CNF:
    return cnf.cnf([clause_or_literal(clause, literal) for clause in cnf1])


def cnf_or_clause(cnf1: cnf.CNF, clause: cnf.Clause) -> cnf.CNF:
    return cnf.cnf([clause_or_clause(clause1, clause) for clause1 in cnf1])


def cnf_or_cnf(cnf1: cnf.CNF, cnf2: cnf.CNF) -> cnf.CNF:
    return ft.reduce(cnf_and_cnf, [cnf_or_clause(cnf1, clause) for clause in cnf2])


# Negation
# ========


def neg_clause(clause: cnf.Clause) -> cnf.CNF:
    return cnf.cnf([cnf.clause([cnf.neg(literal)]) for literal in clause])


def neg_cnf(cnf1: cnf.CNF) -> cnf.CNF:
    return ft.reduce(cnf_or_cnf, [neg_clause(clause) for clause in cnf1])


if __name__ == '__main__':
    logger.info(f'Running {__file__} as a stand-alone script.')
    logger.info('Conjunction between two CNFs:')
    logger.info('>>> cnf_and_cnf(cnf.cnf([[1, 2], [3, 4]]), cnf.cnf([[-1, 5], [6]]))')
    logger.info(cnf_and_cnf(cnf.cnf([[1, 2], [3, 4]]), cnf.cnf([[-1, 5], [6]])))
    logger.info('\n')
    logger.info('Disjunction between two CNFs:')
    logger.info('>>> cnf_or_cnf(cnf.cnf([[1, 2], [3, 4]]), cnf.cnf([[-1, 5], [6]]))')
    logger.info(cnf_or_cnf(cnf.cnf([[1, 2], [3, 4]]), cnf.cnf([[-1, 5], [6]])))
    logger.info('>>> cnf.tautologically_reduce_cnf(_)')
    logger.info(cnf.tautologically_reduce_cnf(cnf_or_cnf(cnf.cnf([[1, 2], [3, 4]]),
                                                         cnf.cnf([[-1, 5], [6]]))))
    logger.info('\n')
    logger.info('Negation of a CNF:')
    logger.info('>>> neg_cnf(cnf.cnf([[1, -2], [2, -3]]))')
    logger.info(neg_cnf(cnf.cnf([[1, -2], [2, -3]])))
    logger.info('>>> cnf.tautologically_reduce_cnf(_)')
    logger.info(cnf.tautologically_reduce_cnf(neg_cnf(cnf.cnf([[1, -2], [2, -3]]))))

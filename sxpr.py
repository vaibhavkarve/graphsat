#!/usr/bin/env python3.8
"""Functions for working with S-expressions.

S-expressions are inspired from ELisp.
"""
# Imports from standard library.
from dataclasses import dataclass
import functools as ft
from typing import Callable, Generic, Tuple, TypeVar, Union
# Imports from third-party modules.
from colorama import Fore, Style  # type: ignore[import]
from loguru import logger
# Import from local modules.
from graphsat.mhgraph import MHGraph


# Type variables and aliases
Src = TypeVar('Src')
Trgt = TypeVar('Trgt')


@dataclass
class Sxpr(Generic[Src, Trgt]):
    """Define generic S-expression."""

    op: Callable[[Trgt, Src], Trgt]  # pylint: disable=invalid-name
    terms: Tuple[Src, ...]
    init: Trgt

    def reduce(self) -> Trgt:
        """Use ft.reduce to evaluate the s-expression.

        Example:
           (+, (1 2 3 4), 0) will evaluate to ((((0 + 1) + 2) + 3) + 4).
        """
        return ft.reduce(self.op, self.terms, self.init)  # type: ignore


class SatSxpr(Sxpr[Src, bool]):  # pylint: disable=too-few-public-methods
    """A subclass of Sxpr[--, bool].

    Args:
       op (:obj:`Callable[[bool, Src], bool]`): This can only be one of two options --
          either `sat_and` or `sat_or`.
       terms (:obj:`Tuple[Src, ...]`): a tuple of terms.

    Returns:
       Computes `init` value based on `op`. Then calls the `__init__` method of `Sxpr`.
    """
    def __init__(self, op: Callable[[bool, Src], bool], terms: Tuple[Src, ...]):
        init: bool
        if op.__name__ == 'sat_and':
            init = True
        elif op.__name__ == 'sat_or':
            init = False
        else:
            raise ValueError(f'Unknown operation {op} encountered')
        super().__init__(op, terms, init)

    def __repr__(self) -> str:  # pragma: no cover
        """Use for pretty-printing an S-expression."""
        if self.op.__name__ == 'sat_and':
            symb: str = ' ∧ '
            color: str = Fore.RED
        elif self.op.__name__ == 'sat_or':
            symb = ' ∨ '
            color = Fore.GREEN
        else:
            symb = ' ? '
            color = ''
            logger.warning(f'Unknown operation {self.op} encountered')

        reset: str = Style.RESET_ALL
        colored_symbol: str = color + symb + reset
        bracket: Tuple[str, str] = (color + "[" + reset, color + "]" + reset)

        if not self.terms:
            return bracket[0] + colored_symbol.join(map(repr, [self.init])) + bracket[1]
        return bracket[0] + colored_symbol.join(map(repr, self.terms)) + bracket[1]


AtomicSxpr = SatSxpr[Union[bool, MHGraph]]


if __name__ == "__main__":
    from time import time

    # conf.logger.remove()
    with logger.catch(message="Something unexpected happened ..."):
        time0 = time()

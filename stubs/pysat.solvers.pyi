#!/usr/bin/env python3.10

from typing import Any, Type
from types import TracebackType

class Minisat22:
    def __init__(self, bootstrap_with: Any = None, use_time: bool = False) -> None:
        ...

    def __enter__(self) -> None: ...

    def __exit__(
        self,
        exc_type: None | Type[BaseException],
        exc_val: None | BaseException,
        exc_tb: None | TracebackType) -> bool: ...

    def solve(self, assumptions: list[Any] = []) -> None | bool: ...

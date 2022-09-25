#!/usr/bin/env python3.10
from typing import Any, Callable

def dispatch(*types: Any, **kwargs: Any) -> Callable[[Any], Any]:
    ...

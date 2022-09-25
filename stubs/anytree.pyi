#!/usr/bin/env python3
from typing import Iterator, Any

class NodeMixin:
    ...


class RenderTree:
    def __init__(self, node: NodeMixin) -> None: ...

    def __iter__(self) -> Iterator[Any]: ...

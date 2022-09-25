#!/usr/bin/env python3.9
"""API for interpreting MHGraphs rewriting as trees.

Each MHGraph starts off as the root of a tree. A rewrite on the graph
creates a bunch of child-nodes such that the original graph is
equisatisfiable to the union of the child nodes. Rewriting when
applied iteratively to the nodes will result in a tree of greater height.

Th graph can be written as being equisatisfiable to the leaves of its
rewrite tree.

"""
from typing import Optional

import anytree as at
import mhgraph as mhg
from graph import Vertex, vertex


class GraphNode(at.NodeMixin):
    """This is a MHGraph that can also act as the node in a tree."""
    def __init__(self,
                 graph: mhg.MHGraph,
                 free: Vertex = vertex(1),
                 parent: Optional[mhg.MHGraph] = None,
                 children: Optional[list[mhg.MHGraph]] = None):
        "Make MHGraph into a node with relevant args."
        self.graph = graph
        self.parent = parent
        self.free = free
        if children:  # set children only if given
            self.children = list(map(GraphNode, children))

    def __str__(self) -> str:
        """Pretty print a tree."""
        lines = []
        for pre, _, node in at.RenderTree(self):
            #pre = ' ' + pre if pre else pre  # add some padding to the front
            line = (f'{pre} {node.graph} '
                    + ("@" + str(node.free) if not node.parent else ""))
            lines.append(line)
        return '\n'.join(lines)

    __repr__ = __str__

# graphsat

A Python package brought to you by [Vaibhav Karve](vaibhavkarve.github.io) and [Anil N. Hirani](https://faculty.math.illinois.edu/~hirani/), Department of Mathematics, University of Illinois at Urbana-Champaign.

We introduce a Python package that recognizes clauses, Cnfs, graphs,
hypergraphs, and multi-hypergraphs. The package implements local
graph-rewriting, graph-satchecking, calculation of graph disjunctions, as
well as checking of new reduction rules.

This package is written in Python v3.9, and is publicly available under an
?? license. It is set to be released on the [Python Packaging
Index](https://pypi.org/) as an open-source scientific package written in
the literate programming style. We specifically chose to write this package
as a literate program, despite the verbosity of this style, with the goal
to create reproducible computational research and ensure that all the
computations are repeatable and the code is reusable.

## Algorithms
Currently, graphsat implements the following algorithms --

- For formulae in conjunctive normal forms (CNFs), it implements variables,
  literals, clauses, Boolean formulae, and truth-assignments. It includes
  an API for reading, parsing and defining new instances.

- For graph theory, the package includes graphs with self-loops,
  edge-multiplicities, hyperedges, and multi-hyperedges. It includes an API
  for reading, parsing and defining new instances.

- For satisfiability of CNFs and graphs, it contains a bruteforce
  algorithm, an implementation that uses the open-source sat-solver
  [PySAT](https://pysathq.github.io/), and an implementation using the
  [MiniSAT](http://minisat.se/) solver.

- Additionally, for graph theory, the library also implements vertex maps,
  vertex degree, homeomorphisms, homomorphisms, subgraphs, and
  isomorphisms. This allows us to encode local rewriting rules as well as
  parallelized grid-based searching for forbidden structures.

- Finally, `graphsat` has a tree-based recursive reduction algorithm that
  uses known local-rewrite rules as well as algorithms for checking
  satisfiability invariance of proposed reduction rules.

## Principles
`graphsat` has been written in the functional-programming style with the
following principles in mind --

- Avoid classes as much as possible. Prefer defining functions instead.

- Write small functions and then compose/map/filter them to create more
  complex functions (using the
  [functools](https://docs.python.org/3/library/functools.html) library).

- Use lazy evaluation strategy whenever possible (using the
  [itertools](https://docs.python.org/3/library/itertools.html) library).

- Add type hints wherever possible (checked using the
  [mypy](https://mypy.readthedocs.io/en/stable/) static type-checker).

- Add unit-tests for each function (checked using the
  [pytest](https://docs.pytest.org/en/latest/) framework).

## Overview of the package
The package consists of several different modules.

1. Modules that act only on Cnfs --

    - `cnf.py` :: Constructors and functions for sentences in conjunctive normal form (Cnf).
    - `cnf_simplify.py` :: Functions for simplifying Cnfs, particularly \((a \vee b \vee c) \wedge (a \vee b \vee \overline{c}) \rightsquigarrow (a \vee b)\).
    - `prop.py` :: Functions for propositional calculus -- conjunction, disjunction and negation.


2. Modules that act only on graphs --

    - `graph.py` :: Constructors and functions for simple graphs.
    - `mhgraph.py` :: Constructors and functions for Loopless-Multi-Hyper-Graphs
    - `morphism.py` :: Constructors and functions for Graph and MHGraph morphisms.

3. Modules concerning SAT and GraphSAT --

    - `sat.py` :: Functions for sat-checking Cnfs, Graphs, MHGraphs.
    - `sxpr.py` :: Functions for working with s-expressions.
    - `operations.py` :: Functions for working with graph-satisfiability and various graph parts.

4. Modules that implement and compute local graph rewriting, rule reduction
   etc.

    - `graph_collapse.py` :: Functions for collapsing a set of Cnfs into compact graphs representation.
    - `graph_rewrite.py` :: An implementation of the Local graph rewriting algorithm.

5. Finally, the test suite for each module is located in the `test/` folder.
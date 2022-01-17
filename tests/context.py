#!/usr/bin/env python3
"""Set the context for avoiding import errors when running the test suite.

Detailed instructions can be found here:
[[https://docs.python-guide.org/writing/structure/]]

"""

import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../graphsat')))

import graphsat # pylint: disable=import-error, wrong-import-position, unused-import

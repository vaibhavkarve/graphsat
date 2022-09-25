#! /usr/bin/env python3.10
"""Initialization module for the `graphsat` package.

This module is executed whenever graphsat or its sub-modules are
imported. This module removes the default logger and adds one with
customized formatter.

"""
import sys

from loguru import logger

# Define a custom formatter string.
CONSOLE_LOGGER_FORMAT: str = ("<green>{time:HH:mm:ss}</green>"
                              " | <level>{level: <8}</level>"
                              " | <cyan>{name: >16}</cyan>:<cyan>{line}</cyan>"
                              " - <level>{message}</level>")

# Remove default logger and add the customized one.
logger.remove()
logger.add(sys.stdout, format=CONSOLE_LOGGER_FORMAT)

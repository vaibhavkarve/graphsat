#!/usr/bin/env python3

from setuptools import setup, find_packages

setup(name='graphsat',
      version='0.1',
      author='Vaibhav Karve',
      author_email='vkarve2@illinois.edu',
      description='A python package for working with Graphs and Satisfiability',
      license='GNU GPLv3',
      keywords='graph, hypergraph, multigraph, typed',
      long_description=read('README'),
      packages=find_packages(),
      classifiers=[
                   'Development Status :: 4 - Beta',
                   'Intended Audience :: Science/Research',
                   'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
                   'Natural Language :: English',
                   'Operating System :: OS Independent',
                   'Programming Language :: Python :: 3.7',
                   'Topic :: Scientific/Engineering :: Mathematics',
                   'Typing :: Typed'
                   ])

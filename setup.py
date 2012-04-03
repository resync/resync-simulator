#!/usr/bin/env python

from setuptools import setup, find_packages

from resyncsim import __version__

setup(
    name = 'resyncsim',
    version = __version__,
    description = "ResourceSyn data source simulator",
    author = "Bernhard Haslhofer",
    author_email = "bernhard.haslhofer@cornell.edu",
    url = "http://www.github.com/behas/resync-simulator",
    packages = find_packages(),
    scripts = ['rs-simulator'],
)
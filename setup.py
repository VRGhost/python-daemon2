# -*- coding: utf-8 -*-

# setup.py
# Part of python-daemon, an implementation of PEP 3143.
#
# Copyright © 2008–2010 Ben Finney <ben+python@benfinney.id.au>
# Copyright © 2008 Robert Niederreiter, Jens Klein
#
# This is free software: you may copy, modify, and/or distribute this work
# under the terms of the Python Software Foundation License, version 2 or
# later as published by the Python Software Foundation.
# No warranty expressed or implied. See the file LICENSE.PSF-2 for details.

""" Distribution setup for python-daemon library.
    """
import imp
import os
import textwrap
from setuptools import setup, find_packages

THIS_DIR = os.path.dirname(os.path.abspath(__file__))

version = imp.load_module("d2_version", *imp.find_module("version", [os.path.join(THIS_DIR, "daemon2")]))

short_description, long_description = (
    textwrap.dedent(d).strip()
    for d in version.description.split(u'\n\n', 1)
    )

setup(
    name=u"python-daemon2",
    version=version.version_short,
    packages=find_packages(exclude=[u"test"]),

    # setuptools metadata
    zip_safe=False,
    test_suite=u"test.suite",
    tests_require=[
        u"MiniMock >=1.2.2",
        ],
    install_requires=[
        u"setuptools",
        u"lockfile >=0.7",
        u"setproctitle",
        u"psutil",
        ],

    # PyPI metadata
    author=", ".join(aut.name for aut in version.authors),
    author_email=version.authors_string,
    description=short_description,
    license=version.license,
    keywords=("daemon", "fork", "unix"),
    url=version.url,
    long_description=long_description,
    classifiers=[
        # Reference: http://pypi.python.org/pypi?%3Aaction=list_classifiers
        u"Development Status :: 4 - Beta",
        u"License :: OSI Approved :: Python Software Foundation License",
        u"Operating System :: POSIX",
        u"Programming Language :: Python",
        u"Intended Audience :: Developers",
        u"Topic :: Software Development :: Libraries :: Python Modules",
        ],
    )

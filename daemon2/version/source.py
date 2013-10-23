# -*- coding: utf-8 -*-

# daemon/version/__init__.py
# Part of python-daemon, an implementation of PEP 3143.
#
# Copyright © 2008–2010 Ben Finney <ben+python@benfinney.id.au>
# This is free software: you may copy, modify, and/or distribute this work
# under the terms of the Python Software Foundation License, version 2 or
# later as published by the Python Software Foundation.
# No warranty expressed or implied. See the file LICENSE.PSF-2 for details.

""" Version information for the python-daemon distribution. """
from datetime import date
from collections import namedtuple

Author = namedtuple("Author", ["name", "email"])

version = (2, 0, 0)
revision = "alpha"
version_string = '.'.join(str(el) for el in version)
version_short = unicode(version_string)
version_full = "{0}.{1!r}".format(version_short, revision)

authors = (
    Author(u"Ben Finney", u"ben+python@benfinney.id.au"),
    Author(u"Ilja Orlovs", u"vrghost@gmail.com"),
)
authors_string = ", ".join(u"{0} <{1}>".format(*el) for el in authors)

copyright_year_begin = u"2001"
copyright_year = date.today().year

copyright_year_range = copyright_year_begin
if copyright_year > copyright_year_begin:
    copyright_year_range += u"–%(copyright_year)s" % vars()

copyright = u"Copyright © {0} {1} and others".format(copyright_year_range, authors_string)
license = u"PSF-2+"

description = """ Library to implement a well-behaved Unix daemon process.

This library implements the well-behaved daemon specification of
:pep:`3143`, "Standard daemon process library".

A well-behaved Unix daemon process is tricky to get right, but the
required steps are much the same for every daemon program. A
`DaemonContext` instance holds the behaviour and configured
process environment for the program; use the instance as a context
manager to enter a daemon state.

Simple example of usage::
    TODO

"""
url = u"http://pypi.python.org/pypi/python-daemon/"
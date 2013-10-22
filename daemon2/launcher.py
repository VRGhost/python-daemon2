# -*- coding: utf-8 -*-

# daemon/daemon.py
# Part of python-daemon, an implementation of PEP 3143.
#
# Copyright © 2008–2010 Ben Finney <ben+python@benfinney.id.au>
# Copyright © 2007–2008 Robert Niederreiter, Jens Klein
# Copyright © 2004–2005 Chad J. Schroeder
# Copyright © 2003 Clark Evans
# Copyright © 2002 Noah Spurrier
# Copyright © 2001 Jürgen Hermann
#
# This is free software: you may copy, modify, and/or distribute this work
# under the terms of the Python Software Foundation License, version 2 or
# later as published by the Python Software Foundation.
# No warranty expressed or implied. See the file LICENSE.PSF-2 for details.

""" Daemon process behaviour.
    """

import os
import logging

import psutil

from . import (
    background,
    exceptions,
    util,
)

log = logging.getLogger(__name__)

class Launcher(object):
    """ Object that launches the `background.Daemon` object instance into the background.

    It also represents foreground daemon interface.
    """

    def __init__(self, pidfile=None):
        """ Set up a new instance. """
        super(Launcher, self).__init__()
        self.pidfile = pidfile

    def start(self, daemon):
        if self.running:
            raise exceptions.DaemonError("Daemon is already running.")
        log.debug("Launching daemon...")

        def _fork(error_message):
            """ Fork a child process, then exit the parent process.

            If the fork fails, raise a ``DaemonProcessDetachError``
            with ``error_message``.

            """
            try:
                return os.fork()
            except OSError, exc:
                raise exceptions.DaemonProcessDetachError(u"{0}: [{1}] {2}".format(
                    error_message, exc.errno, exc.strerror,
                ))

        if _fork(u"Failed first fork"): #_fork(u"Failed first fork"):
            # Original parent
            return
        else:
            # First child
            os.setsid()
            daemon.setupProcessSession()
            pid = _fork(u"Failed second fork")
            try:
                if not pid:
                    # Second child
                    daemon.run(self.pidfile)
                # call _exit for both first and second children
            finally:
                os._exit(0)


    def terminate(self):
        if self.running:
            self.process.terminate()

    @property
    def running(self):
        proc = self.process
        if proc:
            rv = proc.is_running()
        else:
            rv = False
        return rv

    @property
    def process(self):
        pid = self.pid
        if pid:
            rv = psutil.Process(pid)
        else:
            rv = None
        return rv

    @property
    def pid(self):
        if self.pidfile:
            rv = self.pidfile.read_pid()
        else:
            rv = None
        return rv
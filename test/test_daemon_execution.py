import logging
import multiprocessing as mp
import os
import sys
import unittest

import daemon2

log = logging.getLogger(__name__)

class IntegralDaemonTest(unittest.TestCase):

    def setUp(self):
        logging.basicConfig(level=logging.DEBUG)

    def test_daemon_spawn(self):
        startedEvent = mp.Event()
        def _respond():
            log.info("daemon event responds.")
            startedEvent.set()

        lockfile = daemon2.PIDLockFile(os.path.abspath("./test.pid"))
        payload = daemon2.Daemon("test_daemon", target=_respond, stdout=sys.stdout, stderr=sys.stderr)
        daemon = daemon2.Launcher(lockfile)
        daemon.start(payload)
        rv = startedEvent.wait(5)
        self.assertTrue(rv)

    def test_double_daemon_spawn(self):
        startedEvent = mp.Event()
        locks = (
            daemon2.PIDLockFile(os.path.abspath("./test1.pid")),
            daemon2.PIDLockFile(os.path.abspath("./test2.pid"))
        )

        def _daemon1_func():

            def _daemon2_func():
                log.info("daemon event responds.")
                startedEvent.set()

            payload = daemon2.Daemon("test_daemon_2", target=_daemon2_func)
            d2 = daemon2.Launcher(locks[1])
            d2.start(payload)

        payload = daemon2.Daemon("test_daemon_1", target=_daemon1_func, stdout=sys.stdout, stderr=sys.stderr, stdin=sys.stdin)
        daemon1 = daemon2.Launcher(locks[0])
        daemon1.start(payload)

        rv = startedEvent.wait(5)
        self.assertTrue(rv)

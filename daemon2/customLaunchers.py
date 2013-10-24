import os

from lockfile.pidlockfile import PIDLockFile

from . import (
    background,
    launcher,
)

class BoundLauncher(launcher.Launcher):

    backgroundDaemonCls = background.Daemon

    def __init__(self, **kwargs):
        """Daemon launcher that accepts only kwargs and constructs all objects required."""
        try:
            pidfile = kwargs.pop("pidfile")
        except KeyError:
            raise TypeError("{0!r} requires `pidfile` argument.".format(self.__class__.__name__))

        super(BoundLauncher, self).__init__(pidfile=self._makePidfile(pidfile))
        # Pass reminder kwargs to the backgreound daemon object
        self._daemonObject = self.backgroundDaemonCls(**kwargs)

    def start(self, myDaemon=None):
        if myDaemon is not None:
            # the 'daemon' object can be passed by the parents' `restart()` call.
            assert myDaemon is self._daemonObject
        return super(BoundLauncher, self).start(self._daemonObject)

    def restart(self):
        return super(BoundLauncher, self).restart(self._daemonObject)

    def _makePidfile(self, param):
        if isinstance(param, basestring):
            path = os.path.abspath(param)
            if not os.path.isdir(os.path.dirname(path)):
                raise TypeError("{0!r} is not located in the existing directory.".format(path))
            rv = PIDLockFile(path)
        elif hasattr(param, "read_pid"):
            # Assuming param to be pidfile object
            rv = param
        else:
            raise NotImplementedError(param)
        return rv

class CLILauncher(BoundLauncher):

    def act(self, args):
        namespace = self._getParser().parse_args(args)
        self._actNamespace(namespace)

    def _actNamespace(self, namespace):
        # Be a little more forgiving for the cli interface -- ignore duplicate start attempts and such.
        isRunning = self.running
        if namespace.action == "start":
            if not isRunning:
                self.start()
        elif namespace.action == "stop":
            if isRunning:
                self.terminate()
        elif namespace.action == "status":
            print "running" if isRunning else "stopped"
        elif namespace.action == "restart":
            self.restart()
        else:
            raise NotImplementedError(namespace)

    def _getParser(self):
        import argparse
        parser = argparse.ArgumentParser(description="Python daemon command line interface")
        parser.add_argument("action", choices=["start", "stop", "status", "restart"],
            help="Action to be performed")
        return parser

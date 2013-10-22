class DaemonError(Exception):
    """ Base exception class for errors from this module. """

class DaemonOSEnvironmentError(DaemonError, OSError):
    """ Exception raised when daemon OS environment setup receives error. """


class DaemonProcessDetachError(DaemonError, OSError):
    """ Exception raised when process detach fails. """

class DaemonProcessTerminate(DaemonError, SystemExit):
    """Daemon termination exception."""

class DaemonRunnerError(Exception):
    """ Abstract base class for errors from DaemonRunner. """

class DaemonRunnerInvalidActionError(ValueError, DaemonRunnerError):
    """ Raised when specified action for DaemonRunner is invalid. """

class DaemonRunnerStartFailureError(RuntimeError, DaemonRunnerError):
    """ Raised when failure starting DaemonRunner. """

class DaemonRunnerStopFailureError(RuntimeError, DaemonRunnerError):
    """ Raised when failure stopping DaemonRunner. """

class PIDFileError(Exception):
    """ Abstract base class for errors specific to PID files. """

class PIDFileParseError(ValueError, PIDFileError):
    """ Raised when parsing contents of PID file fails. """
# -*- coding: utf-8 -*-

"""Object that represents daemon functionality executed on the daemon side."""
import itertools
import logging
import os
import pty
import setproctitle
import signal

from . import util

log = logging.getLogger(__name__)

class Daemon(object):
    """Object represending daemons' demonic side.

         A `DaemonContext` instance represents the behaviour settings and
        process context for the program when it becomes a daemon. The
        behaviour and environment is customised by setting options on the
        instance, before calling the `open` method.

        Each option can be passed as a keyword argument to the `DaemonContext`
        constructor, or subsequently altered by assigning to an attribute on
        the instance at any time prior to calling `open`. That is, for
        options named `wibble` and `wubble`, the following invocation::

            foo = daemon.DaemonContext(wibble=bar, wubble=baz)
            foo.open()

        is equivalent to::

            foo = daemon.DaemonContext()
            foo.wibble = bar
            foo.wubble = baz
            foo.open()

        The following options are defined.

        `files_preserve`
            :Default: ``None``

            List of files that should *not* be closed when starting the
            daemon. If ``None``, all open file descriptors will be closed.

            Elements of the list are file descriptors (as returned by a file
            object's `fileno()` method) or Python `file` objects. Each
            specifies a file that is not to be closed during daemon start.

        `chroot_directory`
            :Default: ``None``

            Full path to a directory to set as the effective root directory of
            the process. If ``None``, specifies that the root directory is not
            to be changed.

        `working_directory`
            :Default: ``'/'``

            Full path of the working directory to which the process should
            change on daemon start.

            Since a filesystem cannot be unmounted if a process has its
            current working directory on that filesystem, this should either
            be left at default or set to a directory that is a sensible “home
            directory” for the daemon while it is running.

        `umask`
            :Default: ``0``

            File access creation mask (“umask”) to set for the process on
            daemon start.

            Since a process inherits its umask from its parent process,
            starting the daemon will reset the umask to this value so that
            files are created by the daemon with access modes as it expects.

        `pidfile`
            :Default: ``None``

            Context manager for a PID lock file. When the daemon context opens
            and closes, it enters and exits the `pidfile` context manager.

        `signal_map`
            :Default: system-dependent

            Mapping from operating system signals to callback actions.

            The mapping is used when the daemon context opens, and determines
            the action for each signal's signal handler:

            * A value of ``None`` will ignore the signal (by setting the
              signal action to ``signal.SIG_IGN``).

            * Any other value will be used as the action for the
              signal handler. See the ``signal.signal`` documentation
              for details of the signal handler interface.

            The default value depends on which signals are defined on the
            running system. Each item from the list below whose signal is
            actually defined in the ``signal`` module will appear in the
            default map:

            * ``signal.SIGTTIN``: ``None``

            * ``signal.SIGTTOU``: ``None``

            * ``signal.SIGTSTP``: ``None``

            * ``signal.SIGTERM``: ``None``

            Depending on how the program will interact with its child
            processes, it may need to specify a signal map that
            includes the ``signal.SIGCHLD`` signal (received when a
            child process exits). See the specific operating system's
            documentation for more detail on how to determine what
            circumstances dictate the need for signal handlers.

        `uid`
            :Default: ``os.getuid()``

        `gid`
            :Default: ``os.getgid()``

            The user ID (“UID”) value and group ID (“GID”) value to switch
            the process to on daemon start.

            The default values, the real UID and GID of the process, will
            relinquish any effective privilege elevation inherited by the
            process.

        `prevent_core`
            :Default: ``True``

            If true, prevents the generation of core files, in order to avoid
            leaking sensitive information from daemons run as `root`.

        `stdin`
            :Default: ``None``

        `stdout`
            :Default: ``None``

        `stderr`
            :Default: ``None``

            Each of `stdin`, `stdout`, and `stderr` is a file-like object
            which will be used as the new file for the standard I/O stream
            `sys.stdin`, `sys.stdout`, and `sys.stderr` respectively. The file
            should therefore be open, with a minimum of mode 'r' in the case
            of `stdin`, and mode 'w+' in the case of `stdout` and `stderr`.

            If the object has a `fileno()` method that returns a file
            descriptor, the corresponding file will be excluded from being
            closed during daemon start (that is, it will be treated as though
            it were listed in `files_preserve`).

            If ``None``, the corresponding system stream is re-bound to the
            file named by `os.devnull`.
    """

    pidfile = None

    def __init__(self, name, target,
        chroot_directory=None,
        working_directory=u'/',
        umask=0,
        uid=None,
        gid=None,
        prevent_core=True,
        files_preserve=(),
        stdin=None,
        stdout=None,
        stderr=None,
        signal_map=None,
    ):
        super(Daemon, self).__init__()
        self.target = target
        self.name = name

        self.chroot_directory = chroot_directory
        self.working_directory = working_directory
        self.umask = umask
        self.prevent_core = prevent_core
        self.files_preserve = files_preserve
        self.stdin = stdin
        self.stdout = stdout
        self.stderr = stderr

        if uid is None:
            uid = os.getuid()
        self.uid = uid
        if gid is None:
            gid = os.getgid()
        self.gid = gid

        self.signal_map = signal_map or {}


    def run(self, pidfile):
        """Execute the main functionality."""
        self.configureSystem()
        pidfile.acquire(None)
        rc = 254
        try:
            self.setupLogging()
            log.debug("Daemon logging initiated.")
            try:
                self.target()
            except:
                log.exception("Top-level exception.")
                rc = 255
            finally:
                log.debug("Daemon terminated.")
                rc = 0
        finally:
            pidfile.release()
            os._exit(rc)

    def configureSystem(self):
        """OS-level configuration."""
        # Setup signal handlers
        for (sigId, handler) in self.getSignalHandlers():
            signal.signal(sigId, handler)

        setproctitle.setproctitle(self.name)

    def setupLogging(self):
        """Setup logging facilities.

        To be overriden in childern.
        """

    def setupProcessSession(self):
        """Called by launcher to set up process session."""
        if self.chroot_directory is not None:
            util.change_root_directory(self.chroot_directory)

        if self.prevent_core:
            util.prevent_core_dump()

        util.change_file_creation_mask(self.umask)
        util.change_working_directory(self.working_directory)
        util.change_process_owner(self.uid, self.gid)

        # util.close_all_open_files(exclude=self._get_exclude_file_descriptors())

        util.redirect_stream(pty.STDIN_FILENO, self.stdin)
        util.redirect_stream(pty.STDOUT_FILENO, self.stdout)
        util.redirect_stream(pty.STDERR_FILENO, self.stderr)


    def getSignalHandlers(self):
        out = {}
        for (name, handle) in self.signal_map.items():
            sigId = getattr(signal, name)
            if handle:
                out[sigId] = self._getUserSignalHandle(name)
        out[signal.SIGTERM] = self.onTerminateSignal
        return out.items()

    # Signal handlers.
    def onTerminateSignal(self, signal_number, stack_frame):
        """ Signal handler for end-process signals.
        :Return: ``None``

        Signal handler for the ``signal.SIGTERM`` signal. Performs the
        following step:

        * Raise a ``SystemExit`` exception explaining the signal.

        """
        userHandle = self.signal_map.get("SIGTERM")
        try:
            if userHandle:
                userHandle()
        finally:
            raise SystemExit(signal_number)

    def _getUserSignalHandle(self, name):
        def _dummyHandle(signal_number, stack_frame):
            handle = self.signal_map[name]
            handle()
        _dummyHandle.__name__ += "::{0}".format(name)
        return _dummyHandle

    def _get_exclude_file_descriptors(self):
        """ Return the set of file descriptors to exclude closing.

            Returns a set containing the file descriptors for the
            items in `files_preserve`, and also each of `stdin`,
            `stdout`, and `stderr`:

            * If the item is ``None``, it is omitted from the return
              set.

            * If the item has a ``fileno()`` method, that method's
              return value is in the return set.

            * Otherwise, the item is in the return set verbatim.

            """
        all_objs = itertools.chain(
            self.files_preserve,
            [self.stdin, self.stdout, self.stderr]
        )
        out = set()
        for obj in all_objs:
            try:
                handle = obj.fileno
            except AttributeError:
                if isinstance(obj, int):
                    fileno = obj
                elif obj is None:
                    # Ignore None's
                    continue
                else:
                    raise NotImplementedError(obj)
            else:
                fileno = handle()
            out.add(fileno)
        return out

# -*- coding: utf-8 -*-
import os
import sys
import resource
import errno
import signal
import socket

from . import exceptions

def change_working_directory(directory):
    """ Change the working directory of this process.
        """
    try:
        os.chdir(directory)
    except Exception, exc:
        raise exceptions.DaemonOSEnvironmentError(u"Unable to change working directory ({0})".format(
            exc
        ))


def change_root_directory(directory):
    """ Change the root directory of this process.

        Sets the current working directory, then the process root
        directory, to the specified `directory`. Requires appropriate
        OS privileges for this process.

        """
    try:
        os.chdir(directory)
        os.chroot(directory)
    except Exception, exc:
        raise exceptions.DaemonOSEnvironmentError(u"Unable to change root directory ({0})".format(
            exc
        ))

def change_file_creation_mask(mask):
    """ Change the file creation mask for this process.
        """
    try:
        os.umask(mask)
    except Exception, exc:
        raise exceptions.DaemonOSEnvironmentError(u"Unable to change file creation mask ({0})".format(
            exc
        ))


def change_process_owner(uid, gid):
    """ Change the owning UID and GID of this process.

        Sets the GID then the UID of the process (in that order, to
        avoid permission errors) to the specified `gid` and `uid`
        values. Requires appropriate OS privileges for this process.

        """
    try:
        if os.getgid() != gid:
            os.setgid(gid)
        if os.getuid() != uid:
            os.setuid(uid)
    except Exception, exc:
        raise exceptions.DaemonOSEnvironmentError(u"Unable to change file creation mask ({0})".format(
            exc
        ))

def prevent_core_dump():
    """ Prevent this process from generating a core dump.

        Sets the soft and hard limits for core dump size to zero. On
        Unix, this prevents the process from creating core dump
        altogether.

        """
    core_resource = resource.RLIMIT_CORE

    try:
        # Ensure the resource limit exists on this platform, by requesting
        # its current value
        core_limit_prev = resource.getrlimit(core_resource)
    except ValueError, exc:
        raise exceptions.DaemonOSEnvironmentError(u"System does not support RLIMIT_CORE resource limit ({0})".format(
            exc
        ))

    # Set hard and soft limits to zero, i.e. no core dump at all
    core_limit = (0, 0)
    resource.setrlimit(core_resource, core_limit)

MAXFD = 2048

def get_maximum_file_descriptors():
    """ Return the maximum number of open file descriptors for this process.

        Return the process hard resource limit of maximum number of
        open file descriptors. If the limit is “infinity”, a default
        value of ``MAXFD`` is returned.

        """
    limits = resource.getrlimit(resource.RLIMIT_NOFILE)
    result = limits[1]
    if result == resource.RLIM_INFINITY:
        result = MAXFD
    return result


def close_all_open_files(exclude=()):
    """ Close all open file descriptors.

        Closes every file descriptor (if open) of this process. If
        specified, `exclude` is a set of file descriptors to *not*
        close.

        """
    maxfd = get_maximum_file_descriptors()
    fdIter = (fd for fd in reversed(range(maxfd)) if fd not in exclude)
    for fd in fdIter:
        """ Close a file descriptor if already open.

            Close the file descriptor `fd`, suppressing an error in the
            case the file was not open.

            """
        try:
            os.close(fd)
        except OSError, exc:
            if exc.errno == errno.EBADF:
                # File descriptor was not open
                pass
            else:
                raise exceptions.DaemonOSEnvironmentError("Failed to close file descriptor {0} ({1})".format(
                    fd, exc,
                ))

def redirect_stream(target_fileno, stream):
    """ Redirect a system stream to a specified file.

        `system_stream` is a standard system stream such as
        ``sys.stdout``. `target_stream` is an open file object that
        should replace the corresponding system stream object.

        If `target_stream` is ``None``, defaults to opening the
        operating system's null device and using its file descriptor.

        """
    if stream is None:
        target_fd = os.open(os.devnull, os.O_RDWR)
    else:
        target_fd = stream.fileno()
    os.dup2(target_fd, target_fileno)
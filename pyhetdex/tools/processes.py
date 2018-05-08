# Misc python library to support HETDEX software and data analysis
# Copyright (C) 2015, 2016  "The HETDEX collaboration"
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.
"""Multi/single processing abstraction.

Execute functions hiding the information whether are executed in parallel,
using :class:`multiprocessing.pool.Pool` or serially.

The module provides a high level factory function to create and retrieve worker
instances :func:`get_worker`. The first call with a given name creates the
worker, while subsequent calls returns it, ignoring all arguments besides the
name are ignored.

If you need or want to reuse a name after closing the worker, e.g. when using
the worker in a :keyword:`with` statement, you can remove it with
:func:`remove_worker`
"""
from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

import functools
import multiprocessing as mp
import signal
import sys
import time

import six


# =============================================================================
# local variables
# =============================================================================

_workers_dict = {}


# =============================================================================
# Result object to mimic async result and postpone error handling
# =============================================================================

class Result(object):
    """Implements the same interface as
    :class:`multiprocessing.pool.AsyncResult` and execute the function at
    instantiation time.

    Used to abstract single/multi processor cases in :class:`_Worker` and to
    postpone error handling.

    Parameters
    ----------
    func : callable
        function to execute
    args : list
        positional arguments to pass to the function
    kwargs : dict
        keyword arguments to pass to the function
    """
    def __init__(self, func, *args, **kwargs):
        self._ready = True
        try:
            self._value = func(*args, **kwargs)
            self._successful = True
        except Exception:
            self._successful = False
            self._tb = sys.exc_info()

    def get(self, timeout=None):
        """Return the result. If the call raised an exception then that
        exception will be reraised.

        ``timeout`` is ignored.
        """
        if self._successful:
            return self._value
        else:
            six.reraise(*self._tb)

    def wait(self, timeout=None):
        """Do nothing method. Provided for compatibility."""
        pass

    def ready(self):
        """
        Returns
        -------
        bool
            whether the call has completed: always ``True``
        """
        return self._ready

    def successful(self):
        """
        Returns
        -------
        bool
            True whether the call completed without raising an exception
        """
        return self._successful


# =============================================================================
# Result object to mimic async result and postpone function execution
# =============================================================================

class DeferredResult(Result):
    """Reimplement :class:`Result` executing the function in the :meth:`get`
    method.

    Used to abstract single/multi processor cases in :class:`_Worker` to
    postpone function execution.

    Parameters
    ----------
    func : callable
        function to execute
    args : list
        positional arguments to pass to the function
    kwargs : dict
        keyword arguments to pass to the function
    """
    def __init__(self, func, *args, **kwargs):
        self._ready = False
        self._successful = False
        self._function = functools.partial(func, *args, **kwargs)

    def get(self, timeout=None):
        """Execute the function and return its return value(s).

        ``timeout`` is ignored.
        """
        self._ready = True
        result = self._function()
        self._successful = True
        return result


# =============================================================================
# Public interface
# =============================================================================

class WorkerException(Exception):
    """Generic exception"""
    pass


class WorkerNameException(KeyError, WorkerException):
    """The required name does not exist"""
    pass


def get_worker(name='default', multiprocessing=False, always_wait=False,
               poolclass=mp.Pool, result_class=Result, **kwargs):
    """Returns a worker with the specified name.

    At the first call with a given ``name``, the worker is created using the
    remaining arguments. By default the worker is for a single process.
    Subsequent calls with the same ``name`` return always the same worker
    instance and the remaining options are ignored. This means that worker
    instance never need to be passed between different parts of the
    application.

    Parameters
    ----------
    name : string, optional
        name to associate to the :class:`_Worker` object. If does not exist a
        new object is created, stored and returned
    multiprocessing : bool, optional
        use multi processing
    always_wait : bool, optional
        if ``False``, terminate the jobs when exiting the :keyword:`with`
        statement upon an error; if ``True`` wait for the running job to finish
        before closing
    poolclass : class
        class implementing the :class:`multiprocessing.Pool` interface
    result_class : class, optional
        :class:`Result`-like class to use to do the single processor execution
    kwargs : dictionary
        options passed to :class:`multiprocessing.Pool`; ignored if
        ``multiprocessing`` is ``False``

    Returns
    -------
    worker: :class:`_Worker` instance
    """
    try:
        return _workers_dict[name]
    except KeyError:
        worker = _Worker(multiprocessing=multiprocessing,
                         always_wait=always_wait, poolclass=poolclass,
                         result_class=result_class, **kwargs)
        _workers_dict[name] = worker
        return worker


def remove_worker(name='default'):
    """Remove the worker called ``default``

    Parameters
    ----------
    name : string, optional
        name to associate to the pool object.

    Raises
    ------
    WorkerNameException
        if the name does not exist
    """
    try:
        _workers_dict.pop(name)
    except KeyError:
        msg = 'The worker called "{}" does not exist'.format(name)
        raise WorkerNameException(msg)


def ignore_keyboard_interrupt():
    """
    Ignore the KeyboardInterrupt signal
    """
    signal.signal(signal.SIGINT, signal.SIG_IGN)


# =============================================================================
# Class to hide the details of the single or multiprocessor execution
# =============================================================================

class _Worker(object):
    """Class to hide the details of the single or multiprocessor execution. The
    class declaration should be considered as private and should be created and
    retrieved through the :func:`get_worker` factory functions.

    The instance can be used once in a :keyword:`with` statement. Upon exiting,
    it close/terminate and join the pool, if multiprocessing is used.

    Parameters
    ----------
    multiprocessing : bool, optional
        use multi processing
    always_wait : bool, optional
        if ``False``, terminate the jobs when exiting the :keyword:`with`
        statement upon an error; if ``True`` wait for the running job to finish
        before closing
    poolclass : class, optional
        class implementing the :class:`multiprocessing.Pool` interface
    result_class : class, optional
        :class:`Result`-like class to use to do the single processor execution
    kwargs : dictionary
        options passed to :class:`multiprocessing.Pool`; ignored if
        ``multiprocessing`` is ``False``
    """
    def __init__(self, multiprocessing=False, always_wait=False,
                 poolclass=mp.Pool, result_class=Result, **kwargs):
        if multiprocessing:
            self._pool = poolclass(**kwargs)
        else:
            self._pool = None

        self._always_wait = always_wait
        self._result_class = result_class
        # store all the jobs run or applied
        self._jobs = []

    @property
    def pool(self):
        """:class:`multiprocessing.Pool` instance or None, for single processor
        computations"""
        return self._pool

    @property
    def multiprocessing(self):
        """Whether multiprocessing is enabled or not

        Returns
        -------
        bool
        """
        return self._pool is not None

    def __call__(self, func, *args, **kwargs):
        """
        Apply ``func`` on ``args`` and ``kwargs`` (asynchronously if
        multiprocessing is on).

        Parameters
        ----------
        func: callable
            function to execute
        args: list
            positional arguments to pass to the function
        kwargs: dict
            keyword arguments to pass to the function

        Returns
        -------
        job : :class:`~multiprocessing.pool.AsyncResult` or :class:`Result`
            stores the result of the computation can be recovered with the
            :meth:`multiprocessing.pool.AsyncResult.get` or the
            :meth:`Result.get` methods, respectively. The jobs are also stored
            into an internal list and can be accessed with :attr:`jobs` and
            :meth:`get_results`.
        """
        if self._pool is not None:
            # pool.apply_async() returns a ``AsyncResult`` instance. The result
            # can then be retrieved by the get() method.
            job = self._pool.apply_async(func, args, kwargs)
        else:
            job = self._result_class(func, *args, **kwargs)

        self._jobs.append(job)
        return job

    @property
    def jobs(self):
        """ list of :class:`~multiprocessing.pool.AsyncResult` or
        :class:`Result` instances
        """
        return self._jobs

    def clear_jobs(self):
        """Clear the list of jobs
        """
        self._jobs = []

    def get_results(self, fail_safe=False):
        """Wait for all the processes to finish and return the results.

        Parameters
        ----------
        fail_safe : bool
            if any of the jobs raise an exception, capture it and add the
            corresponding instance in the output list instead of the result.
            The default value is to re-raise the exception

        Returns
        -------
        list
            list of the actual results from the computations
        """
        if fail_safe:
            results = []
            for job in self._jobs:
                try:
                    results.append(job.get())
                except Exception as e:
                    results.append(e)
        else:
            results = [job.get() for job in self._jobs]
        return results

    def jobs_stat(self):
        """Return the number of completed jobs

        Returns
        -------
        n_completed : int
            number of completed jobs
        n_error : int
            number of jobs that raised an exception
        n_tot : int
            total number of submitted jobs
        """
        completed = [j for j in self._jobs if j.ready()]
        n_error = sum(not j.successful() for j in completed)

        return len(completed), n_error, len(self._jobs)

    def wait(self, timeout=None):
        """Wait for all the jobs to finish or until ``timeout`` seconds passed

        Parameters
        ----------
        timeout : float, optional
            seconds for the timeout
        """
        if timeout is not None:
            now = time.time()
        new_timeout = timeout

        for j in self._jobs:
            j.wait(timeout=new_timeout)

            # if the timeout is already expired, set it to zero
            if timeout is not None:
                new_now = time.time()
                if new_now - now < timeout:
                    new_timeout = timeout - (new_now - now)
                else:
                    return

    def close(self):
        """Close and join the pool: normal termination"""
        if self._pool is not None:
            self._pool.close()
            self._pool.join()

    def terminate(self):
        """Terminate and join the pool: emergency exit"""
        if self._pool is not None:
            self._pool.terminate()
            self._pool.join()

    def __enter__(self):
        """Entry point for the ``with`` statement"""
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        """Exit point for the with statement

        If there are no errors or ``always_wait`` is ``True`` close, otherwise
        terminate.
        """
        # log the error, just in case
        if not any([exc_type, exc_value, traceback]) or self._always_wait:
            self.close()
        else:
            self.terminate()

"""Multi/single processing abstraction

Execute functions hiding the information whether are executed in parallel,
using :class:`multiprocessing.Pool` or serially.

The module provides a high level factory function to create and retrieve worker
instances :func:`get_worker`

.. todo::
    Warn the user when getting an existing name with the other options not set
    to the defaults

    Add context manager?
"""
from __future__ import print_function

import multiprocessing as mp
import signal
import sys

import six


# =============================================================================
# local variables
# =============================================================================
_workers_dict = {}


# =============================================================================
# Public interface
# =============================================================================
def get_worker(name='default', multiprocessing=False, **kwargs):
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
        name to associate to the pool object. If does not exist an error is
        raised
    multiprocessing : bool, optional
        use multi processing
    kwargs : dictionary
        options passed to :class:`multiprocessing.Pool`; ignored if
        ``multiprocessing`` is ``True``

    Returns
    -------
    worker: :class:`_Worker` instance
    """
    try:
        return _workers_dict[name]
    except KeyError:
        worker = _Worker(multiprocessing=multiprocessing, **kwargs)
        _workers_dict[name] = worker
        return worker


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

    Parameters
    ----------
    multiprocessing : bool, optional
        use multi processing
    kwargs : dictionary
        options passed to :class:`multiprocessing.Pool`; ignored if
        ``multiprocessing`` is ``False``
    """
    def __init__(self, multiprocessing=False, **kwargs):
        if multiprocessing:
            self._pool = mp.Pool(**kwargs)
        else:
            self._pool = None

        # store all the jobs run or applied
        self._jobs = []

    @property
    def pool(self):
        """:class:`multiprocessing.Pool` instance or None, for single processor
        computations"""
        return self._pool

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
            job = Result(func, *args, **kwargs)

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
        return True

    def successful(self):
        """
        Returns
        -------
        bool
            True whether the call completed without raising an exception
        """
        return self._successful

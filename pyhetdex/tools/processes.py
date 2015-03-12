"""Multi/single processing abstraction

Execute functions hiding the information whether are executed in parallel,
using :class:`multiprocessing.Pool` or serially.

The module provides a high level factory function to create and retrieve worker
instances :func:`get_worker`

.. todo::
    Warn the user when getting an existing name with the other options not set
    to the defaults

    Create a mock ``job`` object with :meth:`job.get` for use in single
    processor

    Shut down a pool: :meth:`~multiprocessing.pool.Pool.close`,
    :meth:`~multiprocessing.pool.Pool.terminate` and
    :meth:`~multiprocessing.pool.Pool.join`

    Add context manager?

    Check if we need to deal with ``KeyboardInterrupt`` in multiprocessing
"""

import multiprocessing as mp


# =============================================================================
# local variables
# =============================================================================
_workers_dict = {}


# =============================================================================
# Public interface
# =============================================================================
def get_worker(name='default', multiprocessing=False, processes=None):
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
    processes : None or positive int
        number of processes to launch if multiprocessing is enabled. If
        ``None`` uses :func:`multiprocessing.cpu_count`

    Returns
    -------
    worker: :class:`_Worker` instance
    """
    try:
        return _workers_dict[name]
    except KeyError:
        worker = _Worker(multiprocessing=multiprocessing, processes=processes)
        _workers_dict[name] = worker
        return worker


# =============================================================================
# Class to hide the details of the single or multiprocessor execution
# =============================================================================
class _Worker(object):
    """
    Class to hide the details of the single or multiprocessor execution.
    The class declaration should be considered as private and should be
    accessed only the *create_worker* and *get_worker* factory functions. The
    public class methods should be considered as such

    Initialize the multiprocessing pool (if required) and the job list.
    Otherwise the pool is None

    Parameters
    ----------
    multiprocessing : bool, optional
        use multi processing
    processes : None or positive int
        number of processes to launch if multiprocessing is enabled. If
        ``None`` uses :func:`multiprocessing.cpu_count`
    """

    def __init__(self, multiprocessing=False, processes=None):
        if multiprocessing:
            self.pool = mp.Pool(processes=processes,
                                initializer=self._init_worker)
        else:
            self.pool = None

    def _init_worker(self):
        """
        Ignore the KeyboardInterrupt signal during multiprocessing the signal
        is handled outside.

        .. todo::
            deal with KeyboardInterrupt as in examples `here
            <https://github.com/jreese/multiprocessing-keyboardinterrupt/blob/master/example.py>`_
            and `here
            <http://bryceboe.com/2010/08/26/python-multiprocessing-and-keyboardinterrupt/>`_
            and in :func:`quicklook.src.errors:TerminationHandler`
        """
        import signal
        signal.signal(signal.SIGINT, signal.SIG_IGN)

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
        job : result
            output of ``func`` or an instance of
            :class:`multiprocessing.pool.AsyncResult`, if multiprocessing is
            enabled. In the latter case the result can be accessed with
            :meth:`~multiprocessing.pool.AsyncResult.get`.
        """
        if self.pool:
            # A object is returned by the
            # pool.apply_async() function. The result can then be retrieved by
            # the get() method.
            job = self.pool.apply_async(func, args, kwargs)
        else:
            job = func(*args, **kwargs)

        return job

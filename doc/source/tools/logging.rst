.. :py:currentmodule:: pyhetdex.tools.logging_helper

:py:mod:`logging_helper` -- Logging extensions and helpers
**********************************************************

.. automodule:: pyhetdex.tools.logging_helper

Examples
========

First the imports:

.. doctest::

    >>> import multiprocessing as mp
    >>> import logging
    >>> import sys
    >>> import pyhetdex.tools.logging_helper as phlog
    >>> import pyhetdex.tools.processes as p

and some utility functions

.. doctest::

    >>> # initialise the logger and the QueueHandler
    >>> def init_logger(queue, name):
    ...     qhandler = phlog.QueueHandler(queue)
    ...     qhandler.setLevel(logging.INFO) 
    ...     logger = logging.getLogger(name)
    ...     logger.setLevel(logging.INFO) 
    ...     logger.addHandler(qhandler)
    ...     return logger
    >>> # create the stdout handler
    >>> def stdout_handler(fmt=None):
    ...     shandler = logging.StreamHandler(stream=sys.stdout)
    ...     if fmt is None:
    ...         fmt = "[%(levelname)s] %(message)s"
    ...     shandler.setFormatter(logging.Formatter(fmt=fmt))
    ...     shandler.setLevel(logging.INFO) 
    ...     return shandler
    >>> # function to execute in the worker pool
    >>> def log_func(name, level, message):
    ...     logger = logging.getLogger(name)
    ...     logger.log(level, message)

Logging from the main process
-----------------------------

This example show how to setup the
:class:`~pyhetdex.tools.logging_helper.QueueHandler` and
:class:`~pyhetdex.tools.logging_helper.QueueListener` to log from the main
process to standard output via a queue. Although this is a bit of overkill for
current the example, it could be useful if any of the handlers can blocks, like
if it needs an internet connection.

.. doctest::
    
    >>> # create the logger and add the QueueHandler
    >>> logger_name = "single_proc"
    >>> q_sp = mp.Queue()
    >>> logger = init_logger(q_sp, logger_name)
    >>> # start the QueueListener and log two messages
    >>> with phlog.SetupQueueListener(q_sp, handlers=[stdout_handler()],
    ...                               use_process=False):
    ...     logger.info("this is a demonstration")
    ...     logger.error("this is an error")
    [INFO] this is a demonstration
    [ERROR] this is an error
    >>> q_sp.close()


Logging from subprocesses
-------------------------

This way of logging becomes even more useful if you want to log to a common
place from multiple processes. First, it avoids logging multiple messages at the
same time, which can corrupt them; secondly it avoids that, when using e.g. the
:class:`logging.handlers.RotatingFileHandlers`, multiple handlers try to
move/rename/remove the same log file at the same time.

.. doctest::
    
    >>> logger_name = "multi_proc"
    >>> q_mp = mp.Queue()
    >>> # create a multiprocessing worker
    >>> worker = p.get_worker(name="multip", multiprocessing=True,
    ...                       initializer=init_logger,
    ...                       initargs=(q_mp, logger_name))
    >>> # start the QueueListener and run two jobs
    >>> with phlog.SetupQueueListener(q_mp, handlers=[stdout_handler()],
    ...                               use_process=True):
    ...     worker(log_func, logger_name, logging.INFO, "this is a demonstration")
    ...     worker(log_func, logger_name, logging.ERROR, "this is an error")
    ...     worker.get_results()  # doctest: +SKIP
    ...     worker.close()
    [INFO] this is a demonstration
    [ERROR] this is an error
    >>> q_mp.close()

:py:class:`QueueHandler` -- Put log records to a queue
======================================================

.. autoclass:: pyhetdex.tools.logging_helper.QueueHandler
    :member-order: groupwise
    :members:
    :undoc-members:
    :private-members:
    :show-inheritance:


:py:class:`QueueListener` -- Log records from a queue
=====================================================

.. autoclass:: pyhetdex.tools.logging_helper.QueueListener
    :member-order: groupwise
    :members:
    :undoc-members:
    :private-members:
    :show-inheritance:

:py:class:`SetupQueueListener` -- Setup the :class:`QueueListener`
==================================================================

.. autoclass:: pyhetdex.tools.logging_helper.SetupQueueListener
    :member-order: groupwise
    :members:
    :special-members: __enter__, __exit__
    :show-inheritance:

.. :py:currentmodule:: pyhetdex.tools.logging

:py:mod:`logging` -- Logging extensions and helpers
===================================================

.. automodule:: pyhetdex.tools.logging_helper

Examples
--------

.. doctest::

    >>> import multiprocessing as mp
    >>> import logging
    >>> import sys
    >>> import pyhetdex.tools.logging_helper as phlog
    >>> import pyhetdex.tools.processes as p

Log from the main process to a listener in a thread. Can help with blocking
handlers, like handlers that require network connection or that send mails.

.. doctest::
    
    >>> # create the logger and add the QueueHandler
    >>> logger_name = "single_proc"
    >>> q_sp = mp.Queue()
    >>> qhandler = phlog.QueueHandler(q_sp)
    >>> logger = logging.getLogger(logger_name)
    >>> logger.setLevel(logging.INFO) 
    >>> logger.addHandler(qhandler)
    >>> # create a stdout handler
    >>> shandler = logging.StreamHandler(stream=sys.stdout)
    >>> fmt = "[%(levelname)s] %(message)s"
    >>> shandler.setFormatter(logging.Formatter(fmt=fmt))
    >>> shandler.setLevel(logging.INFO) 
    >>> # start the QueueListener and log two messages
    >>> with phlog.SetupQueueListener(q_sp, handlers=[shandler],
    ...                               use_process=False):
    ...     logger.info("this is a demonstration")
    ...     logger.error("this is an error")
    [INFO] this is a demonstration
    [ERROR] this is an error
    >>> q_sp.close()

Log from multiple processes without mangling the log messages

.. doctest::
    
    >>> logger_name = "multi_proc"
    >>> q_mp = mp.Queue()
    >>> # function to initialise the logger and the QueueHandler
    >>> def init_logger(queue, name):
    ...      qhandler = phlog.QueueHandler(queue)
    ...      logger = logging.getLogger(name)
    ...      logger.setLevel(logging.INFO) 
    ...      logger.addHandler(qhandler)
    >>> # create a stdout handler
    >>> shandler = logging.StreamHandler(stream=sys.stdout)
    >>> fmt = "[%(levelname)s - %(process)d] %(message)s"
    >>> shandler.setFormatter(logging.Formatter(fmt=fmt))
    >>> shandler.setLevel(logging.INFO) 
    >>> # create a multiprocessing worker
    >>> worker = p.get_worker(name="multip", multiprocessing=True,
    ...                       initializer=init_logger,
    ...                       initargs=(q_mp, logger_name))
    >>> # function to execute in the worker pool
    >>> def log_func(name, level, message):
    ...     logger = logging.getLogger(name)
    ...     logger.log(level, message)
    >>> # start the QueueListener and run two jobs
    >>> with phlog.SetupQueueListener(q_mp, handlers=[shandler],
    ...                               use_process=True):
    ...     worker(log_func, logger_name, logging.INFO, "this is a demonstration")
    ...     worker(log_func, logger_name, logging.ERROR, "this is an error")
    ...     worker.get_results()  # doctest: +SKIP
    ...     worker.close()
    [INFO] this is a demonstration
    [ERROR] this is an error
    >>> q_mp.close()



:py:class:`QueueHandler` -- Put log records to a queue
------------------------------------------------------

.. autoclass:: pyhetdex.tools.logging_helper.QueueHandler
    :member-order: groupwise
    :members:
    :undoc-members:
    :private-members:
    :show-inheritance:


:py:class:`QueueListener` -- Log records from a queue
-----------------------------------------------------

.. autoclass:: pyhetdex.tools.logging_helper.QueueListener
    :member-order: groupwise
    :members:
    :undoc-members:
    :private-members:

:py:class:`SetupQueueListener` -- Setup the :class:`QueueListener`
------------------------------------------------------------------

.. autoclass:: pyhetdex.tools.logging_helper.SetupQueueListener
    :member-order: groupwise
    :members:
    :undoc-members:
    :private-members:

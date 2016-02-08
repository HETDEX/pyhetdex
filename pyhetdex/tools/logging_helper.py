# The original implementation of QueueHandler and QueueListener
# Copyright 2001-2015 by Vinay Sajip. All Rights Reserved.
#
# Permission to use, copy, modify, and distribute this software and its
# documentation for any purpose and without fee is hereby granted,
# provided that the above copyright notice appear in all copies and that
# both that copyright notice and this permission notice appear in
# supporting documentation, and that the name of Vinay Sajip
# not be used in advertising or publicity pertaining to distribution
# of the software without specific, written prior permission.
# VINAY SAJIP DISCLAIMS ALL WARRANTIES WITH REGARD TO THIS SOFTWARE, INCLUDING
# ALL IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS. IN NO EVENT SHALL
# VINAY SAJIP BE LIABLE FOR ANY SPECIAL, INDIRECT OR CONSEQUENTIAL DAMAGES OR
# ANY DAMAGES WHATSOEVER RESULTING FROM LOSS OF USE, DATA OR PROFITS, WHETHER
# IN AN ACTION OF CONTRACT, NEGLIGENCE OR OTHER TORTIOUS ACTION, ARISING OUT
# OF OR IN CONNECTION WITH THE USE OR PERFORMANCE OF THIS SOFTWARE.

"""Backports, extensions and customisations of the logging system

Use examples for :class:`QueueHandler` and :class:`QueueListener` can be found
`here
<https://docs.python.org/3/howto/logging-cookbook.html#dealing-with-handlers-that-block>`_,
`here
<https://docs.python.org/3/howto/logging-cookbook.html#logging-to-a-single-file-from-multiple-processes>`_
and `here
<https://docs.python.org/3/howto/logging-cookbook.html#a-more-elaborate-multiprocessing-example>`_.

:class:`QueueHandler` and :class:`QueueListener` are copied from the `cPython
3.5 branch <https://hg.python.org/cpython>`_ commit ``9aee273bf8b7`` and
slightly modified (mostly documentation).
"""
from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

import logging
try:
    import threading
except ImportError:  # pragma: no cover
    threading = None
import traceback as tb


import pyhetdex.tools.queue as phqueue


class QueueHandler(logging.Handler):
    """
    This handler sends events to a queue. Typically, it would be used together
    with a multiprocessing Queue to centralise logging to file in one process
    (in a multi-process application), so as to avoid file write contention
    between processes.

    This code is new in Python 3.2, but this class can be copy pasted into
    user code for use with earlier Python versions.

    Parameters
    ----------
    queue : queue-like instance
    """

    def __init__(self, queue):
        """
        Initialise an instance, using the passed queue.
        """
        logging.Handler.__init__(self)
        self.queue = queue

    def enqueue(self, record):
        """
        Enqueue a record.

        The base implementation uses ``put_nowait``. You may want to override
        this method if you want to use blocking, timeouts or custom queue
        implementations.
        """
        self.queue.put_nowait(record)

    def prepare(self, record):
        """
        Prepares a record for queuing. The object returned by this method is
        enqueued.

        The base implementation formats the record to merge the message
        and arguments, and removes unpickleable items from the record
        in-place.

        You might want to override this method if you want to convert
        the record to a dict or JSON string, or send a modified copy
        of the record while leaving the original intact.
        """
        # The format operation gets traceback text into record.exc_text
        # (if there's exception data), and also puts the message into
        # record.message. We can then use this to replace the original
        # msg + args, as these might be unpickleable. We also zap the
        # exc_info attribute, as it's no longer needed and, if not None,
        # will typically not be pickleable.
        self.format(record)
        record.msg = record.message
        record.args = None
        record.exc_info = None
        return record

    def emit(self, record):
        """
        Emit a record.

        Writes the LogRecord to the queue, preparing it for pickling first.
        """
        try:
            self.enqueue(self.prepare(record))
        except Exception:
            self.handleError(record)


if threading:
    class QueueListener(phqueue.QueueListener):
        """
        This class implements an internal threaded listener which watches for
        LogRecords being added to a queue, removes them and passes them to a
        list of handlers for processing.

        Parameters
        ----------
        queue_ : queue-like instance
        handlers : list of :class:`logging.Handler` child instances
        respect_handler_level : bool, optional
            if ``True`` the handler's level is respected
        """
        _sentinel = None

        def __init__(self, queue_, handlers=[], respect_handler_level=False):
            super(QueueListener, self).__init__(queue_)
            self.handlers = handlers
            self.respect_handler_level = respect_handler_level

        def handle(self, record):
            """
            Handle a record.

            This just loops through the handlers offering them the record
            to handle.
            """
            record = self.prepare(record)
            for handler in self.handlers:
                if not self.respect_handler_level:
                    do_process = True
                else:
                    do_process = record.levelno >= handler.level
                if do_process:
                    handler.handle(record)


# Setup and stop a QueueListener in as separate process

class SetupQueueListener(phqueue.SetupQueueListener):
    """Start the :class:`QueueListener`, in a separate process if required.

    Adapted from `logging cookbook
    <https://docs.python.org/3/howto/logging-cookbook.html#a-more-elaborate-multiprocessing-example>`_.

    The :class:`SetupQueueListener` instance can be used as a context manager
    for a :keyword:`with` statement. Upon exiting the statement, the process
    and :class:`QueueListener` are stopped. If an exception happens, it will be
    logged as critical before stopping: in order to avoid possible errors with
    missing formatter keywords, the handler formatters are temporarily
    substituted with "%(level)s %(message)s".

    Parameters
    ----------
    queue_ : queue-like object
        queue which contains messages to log
    handlers : list of :class:`logging.Handler` child instances
    respect_handler_level : bool, optional
        if ``True`` the handler's level is respected
    use_process : bool, optional
        if ``True`` start the listener in a separate process

    Attributes
    ----------
    queue, handlers : as above
    stop_event : :class:`multiprocessing.Event` instance
        event used to signal to stop the listener
    lp : :class `multiprocessing.Process` instance
        process running the listener, if ``use_process`` is ``True``
    listener : :class:`QueueListener` instance
    """
    def __init__(self, queue_, handlers=[], respect_handler_level=True,
                 use_process=True):
        qlc_kwargs = {'handlers': handlers,
                      'respect_handler_level': respect_handler_level}
        super(SetupQueueListener, self).__init__(QueueListener, queue_,
                                                 use_process=use_process,
                                                 qlc_kwargs=qlc_kwargs)
        self.handlers = handlers

    def __exit__(self, exc_type, exc_value, traceback):
        """Exit point for the with statement

        Temporary change the formatter of the handlers to avoid errors in case
        of custom formatter keys
        """
        self.stop()  # stop the listener

        # log the error, just in case
        if any([exc_type, exc_value, traceback]):
            # create new record
            straceback = "".join(tb.format_exception(exc_type, exc_value,
                                 traceback))[:-1]  # remove last newline
            msg = """Emergency exit from the QueueListener\n"""
            msg += straceback
            record = logging.LogRecord("emergency", logging.CRITICAL, "", 0,
                                       msg, (), ())
            # save old formatters
            formatters = [h.formatter for h in self.handlers]
            # set new default formatters
            fmt = "%(levelname)s %(message)s"
            for h in self.handlers:
                h.setFormatter(logging.Formatter(fmt=fmt))

            listener = self._start_listener()
            self.queue.put_nowait(record)
            listener.stop()
            # reset the formatters, just in case
            for h, fmt in zip(self.handlers, formatters):
                h.setFormatter(fmt)

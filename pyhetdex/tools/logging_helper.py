# for QueueHandler and QueueListener implementation
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

import logging
import multiprocessing
try:
    import threading
except ImportError:  # pragma: no cover
    threading = None
import traceback as tb

from six.moves import queue


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
    class QueueListener(object):
        """
        This class implements an internal threaded listener which watches for
        LogRecords being added to a queue, removes them and passes them to a
        list of handlers for processing.

        This code is new in Python 3.2

        Parameters
        ----------
        queue : queue-like instance
        handlers : list of :class:`logging.Handler` child instances
        respect_handler_level : bool, optional
            if ``True`` the handler's level is respected
        """
        _sentinel = None

        def __init__(self, queue, handlers=[], respect_handler_level=False):
            self.queue = queue
            self.handlers = handlers
            self._stop = threading.Event()
            self._thread = None
            self.respect_handler_level = respect_handler_level

        def dequeue(self, block):
            """
            Dequeue a record and return it, optionally blocking.

            The base implementation uses get. You may want to override this
            method if you want to use timeouts or work with custom queue
            implementations.
            """
            return self.queue.get(block)

        def start(self):
            """
            Start the listener.

            This starts up a background thread to monitor the queue for
            LogRecords to process.
            """
            self._thread = t = threading.Thread(target=self._monitor)
            t.setDaemon(True)
            t.start()

        def prepare(self, record):
            """
            Prepare a record for handling.

            This method just returns the passed-in record. You may want to
            override this method if you need to do any custom marshalling or
            manipulation of the record before passing it to the handlers.
            """
            return record

        def handle(self, record):
            """
            Handle a record.

            This just loops through the handlers offering them the record
            to handle.
            """
            record = self.prepare(record)
            for handler in self.handlers:
                if not self.respect_handler_level:
                    process = True
                else:
                    process = record.levelno >= handler.level
                if process:
                    handler.handle(record)

        def _monitor(self):
            """
            Monitor the queue for records, and ask the handler
            to deal with them.

            This method runs on a separate, internal thread.
            The thread will terminate if it sees a sentinel object in the
            queue.
            """
            q = self.queue
            has_task_done = hasattr(q, 'task_done')
            while not self._stop.isSet():
                try:
                    record = self.dequeue(True)
                    if record is self._sentinel:
                        break
                    self.handle(record)
                    if has_task_done:
                        q.task_done()
                except queue.Empty:
                    pass
            # There might still be records in the queue.
            while True:
                try:
                    record = self.dequeue(False)
                    if record is self._sentinel:
                        break
                    self.handle(record)
                    if has_task_done:
                        q.task_done()
                except queue.Empty:
                    break

        def enqueue_sentinel(self):
            """
            This is used to enqueue the sentinel record.

            The base implementation uses put_nowait. You may want to override
            this method if you want to use timeouts or work with custom queue
            implementations.
            """
            self.queue.put_nowait(self._sentinel)

        def stop(self):
            """
            Stop the listener.

            This asks the thread to terminate, and then waits for it to do so.
            Note that if you don't call this before your application exits,
            there may be some records still left on the queue, which won't be
            processed.
            """
            self._stop.set()
            self.enqueue_sentinel()
            self._thread.join()
            self._thread = None


# Setup and stop a QueueListener in as separate process
class SetupQueueListener(object):
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
        self.queue = queue_
        self.handlers = handlers
        self.respect_level = respect_handler_level
        self.stop_event = multiprocessing.Event()
        if use_process:
            self.lp = multiprocessing.Process(target=self._listener_process,
                                              name='listener')
            self.lp.start()
        else:
            self.listener = self._start_listener()

    def stop(self):
        """Stop the listener and, if it's running in a process, join it. Should
        be called before the main process finishes to avoid losing logs."""
        try:
            self.stop_event.set()
            self.lp.join()
        except AttributeError:  # if threading is used
            self.listener.stop()

    def _listener_process(self):
        """This initialises logging with the given handlers.

        To be used in a separate process.

        Starts the listener and waits for the main process to signal completion
        via the event. The listener is then stopped.
        """
        listener = self._start_listener()

        self.stop_event.wait()
        listener.stop()

    def _start_listener(self):
        """Create, start and return the listener"""
        listener = QueueListener(self.queue, handlers=self.handlers,
                                 respect_handler_level=self.respect_level)
        listener.start()

        return listener

    def __enter__(self):
        """Entry point for the ``with`` statement"""
        return self

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

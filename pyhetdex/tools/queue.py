"""Common functionalities related with queue and queue listeners

:class:`QueueListener` is a abstract base class that provides a threaded
listener that extract items from a queue and handle them. The only method that
needs to be implemented is :meth:`QueueListener.handle`. The implementation is
adapted from `cPython 3.5 branch <https://hg.python.org/cpython>`_ commit
``9aee273bf8b7``

The :class:`SetupQueueListener` is a helper class that accept a class derived
from :class:`QueueListener`, a queue and a number of other arguments, and
starts the queue listener, optionally in a separate process. The class also
provides a context manager interfaces, that stop the thread, and the process,
where the :class:`QueueListener` is running. The implementation is based on
`logging cookbook
<https://docs.python.org/3/howto/logging-cookbook.html#a-more-elaborate-multiprocessing-example>`_.

"""

from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

import abc
import multiprocessing
from multiprocessing.queues import Queue
import threading

import six
from six.moves import queue


class QueueContext(Queue):
    """Add a context manager to the :class:`multiprocessing.queues.Queue`

    Parameters
    ----------
    maxsize : int, optional
        sets the upper bound limit on the number of items
        that can be placed in the queue. Insertion will block once this size
        has been reached, until queue items are consumed. If ``maxsize`` is
        less than or equal to zero, the queue size is infinite.
    """
    def __init__(self, maxsize=0):
        kwargs = {'maxsize': maxsize}

        if not six.PY2:
            kwargs['ctx'] = multiprocessing.get_context()

        super(QueueContext, self).__init__(**kwargs)

    def __enter__(self):
        """Returns an instance of the queue"""
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        """Close and join the thread where the queue lives"""
        self.close()
        self.join_thread()


if threading:
    @six.add_metaclass(abc.ABCMeta)
    class QueueListener(object):
        """
        This class implements an internal threaded listener which watches for
        entries being added to a queue, removes them and passes them to a
        handler method, that subclasses must re-implement.

        Parameters
        ----------
        queue : queue-like instance
        """
        _sentinel = None

        def __init__(self, queue):
            self.queue = queue
            self._stop = threading.Event()
            self._thread = None

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
            records to process
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

        @abc.abstractmethod
        def handle(self, record):
            """
            Handle a record.

            Abstract method: this method must be implemented in derived
            classes.

            Parameters
            ----------
            record :
                record to handle

            Returns
            -------
            record :
                record after passing through :meth:`prepare`.
            """
            record = self.prepare(record)
            return record

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

            The base implementation uses ``put_nowait``. You may want to
            override this method if you want to use timeouts or work with
            custom queue implementations.
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
    """Start the ``qlc``, in a separate process if required.


    The :class:`SetupQueueListener` instance can be used as a context manager
    for a :keyword:`with` statement.

    Parameters
    ----------
    qlc : :class:`QueueListener` child
        class to instantiate in the setup
    queue_ : queue-like object
        qeueu to pass as first argument to ``qlc``
    qlc_args : list
        arguments to pass to the ``qlc`` when instantiating it
    qlc_kwargs : dict
        keyword arguments to pass to the ``qlc`` when instantiating it
    use_process : bool, optional
        if ``True`` start the listener in a separate process

    Attributes
    ----------
    queue : as above
    stop_event : :class:`multiprocessing.Event` instance
        event used to signal to stop the listener
    lp : :class `multiprocessing.Process` instance
        process running the listener, if ``use_process`` is ``True``
    listener : ``qlc`` instance
    """
    def __init__(self, qlc, queue_, use_process=True, qlc_args=(),
                 qlc_kwargs={}):
        self._qlc = qlc
        self._qlc_args = qlc_args
        self._qlc_kwargs = qlc_kwargs
        self.queue = queue_
        self.stop_event = multiprocessing.Event()
        if use_process:
            self.lp = multiprocessing.Process(target=self._listener_process,
                                              name='listener')
            self.lp.start()
        else:
            self.listener = self._start_listener()

    def stop(self):
        """Stop the listener and, if it's running in a process, join it. Should
        be called before the main process finishes to avoid losing messages."""
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
        listener = self._qlc(self.queue, *self._qlc_args, **self._qlc_kwargs)
        listener.start()

        return listener

    def __enter__(self):
        """Entry point for the ``with`` statement

        Returns
        -------
        self
        """
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        """Exit point for the with statement

        The base implementation call :meth:`stop`
        """
        self.stop()  # stop the listener

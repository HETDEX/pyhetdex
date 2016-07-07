"""Test the queues"""

from multiprocessing import Process, Manager

import pytest
from six.moves import queue

import pyhetdex.tools.queue as phqueue


class QueueListenerList(phqueue.QueueListener):
    """Implementation storing the output in a list"""
    def __init__(self, queue, list_):
        super(QueueListenerList, self).__init__(queue)
        self.list_ = list_

    def handle(self, record):
        record = super(QueueListenerList, self).handle(record)
        self.list_.append(record)


@pytest.yield_fixture
def queue_in_process():
    """Create a process running a function that put some data into a
    :class:`libvhc.utils.QueueContext` queue.
    Yields the queue and the object passed to the queue.
    After the yield, join the process
    """
    def f(q_, msg_):
        q_.put(msg_)

    q = phqueue.QueueContext()
    msg = [42, 'is the', 'answer', None]
    p = Process(target=f, args=(q, msg))
    p.start()
    yield q, msg
    p.join()


def test_queue_context(queue_in_process):
    "Test that the queue in the context manager behaves correctly"
    with queue_in_process[0] as queue:
        msg = queue.get()
        assert msg == queue_in_process[1]


@pytest.mark.xfail(raises=AssertionError,
                   reason="It's not possible to put stuff in the queue after"
                          " closing it")
def test_queue_context_after_close(queue_in_process):
    "Test that the queue correctly fails after closing it"

    with queue_in_process[0] as queue:
        pass

    queue.put("not in the context")


@pytest.mark.xfail(raises=TypeError,
                   reason="It's not possible to instantiate an abstract class")
def test_abc_instantiation():
    phqueue.QueueListener(phqueue.QueueContext())


@pytest.mark.parametrize('q', [phqueue.QueueContext, queue.Queue])
def test_override(q):
    """Test overriding of the QueueListener with different queue types"""
    n_elements = 4
    q_ = q()
    listener = QueueListenerList(q_, [])
    listener.start()
    for i in range(n_elements):
        q_.put(i)

    listener.stop()

    assert len(listener.list_) == n_elements
    assert listener.list_ == list(range(n_elements))

    try:  # mark that the task has been done to avoid locking the test
        q_.task_done()
        q_.join()
    except AttributeError:
        q_.close()
        q_.join_thread()


@pytest.mark.parametrize('use_process', [True, False])
def test_setup_queue_listener(use_process):
    """test that the process is correctly setup and teared down"""
    n_elements = 4
    list_ = Manager().list()
    q = phqueue.QueueContext()
    listener = phqueue.SetupQueueListener(QueueListenerList, q,
                                          qlc_args=(list_, ),
                                          use_process=use_process)
    with q, listener:
        for i in range(n_elements):
            q.put(i)

    assert len(list_) == n_elements
    assert list(list_) == list(range(n_elements))

"""Test pyhetdex.tools.logging_helper"""
from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

import itertools as it
import logging
import multiprocessing
import os
import re
import uuid

import pytest

import pyhetdex.tools.logging_helper as phlog
import pyhetdex.tools.processes as phproc

parametrize = pytest.mark.parametrize


@pytest.fixture
def logger_level():
    '''Default logger level: INFO'''
    return logging.INFO


@pytest.yield_fixture
def qhandler():
    '''Create and yield a multiprocessing queue and a QueueHandler
    The queue closed after the yield
    '''
    q = multiprocessing.Queue()
    qhandler = phlog.QueueHandler(q)

    yield q, qhandler

    q.close()


@pytest.fixture
def logger():
    '''create and returns a logger of the ``logger_level``. Use a random name
    for the logger'''
    logger = logging.getLogger(name=str(uuid.uuid4().hex)[:10])
    logger.setLevel(logging.DEBUG)
    return logger


@pytest.fixture
def list_handler(logger_level):
    '''Create a fake handler that stores are record in a list and with level
    set by ``logger_level``. Returns an instance of the class and the lists in
    which records and the changed formatters are registered'''
    record_list = multiprocessing.Manager().list()
    formatter_list = multiprocessing.Manager().list()

    class ListHandler(object):
        level = logger_level
        formatter = 'the formatter'

        def handle(self, record):
            record_list.append(record)

        def setFormatter(self, formatter):
            'Save the formatter'
            self.formatter = formatter
            formatter_list.append(formatter)

    return ListHandler(), record_list, formatter_list


@parametrize('use_process', [False, True])
@parametrize('respect_handler_level, n_logs', [(True, 1), (False, 2)])
def test_setup_queue_listener(qhandler, logger, logger_level, list_handler,
                              use_process, respect_handler_level, n_logs):
    """QueueHandler and QueueListener in the same process
    """
    logger.addHandler(qhandler[1])

    with phlog.SetupQueueListener(qhandler[0], handlers=[list_handler[0], ],
                                  use_process=use_process,
                                  respect_handler_level=respect_handler_level):
        logger.log(logger_level + 1, 'Above level')
        logger.log(logger_level - 1, 'Below level')

    assert len(list_handler[1]) == n_logs
    record = list_handler[1][0]
    assert record.levelno > logger_level


def test_setup_queue_listener_exit_logger(caplog, qhandler, logger,
                                          logger_level, list_handler):
    """Raise an error in the SetupQueueListener and check that the error is
    properly handled
    """
    logger.addHandler(qhandler[1])
    original_formatter = list_handler[0].formatter
    try:
        with phlog.SetupQueueListener(qhandler[0],
                                      handlers=[list_handler[0], ]):
            logger.log(logger_level + 1, 'Above level')
            raise RuntimeError("test how __exit__ deal with errors")
    except RuntimeError:
        pass

    assert len(list_handler[1]) == 2
    record = list_handler[1][0]
    assert record.levelno > logger_level
    record = list_handler[1][1]
    assert record.levelname == 'CRITICAL'

    assert len(list_handler[2]) == 2
    assert isinstance(list_handler[2][0], logging.Formatter)
    assert list_handler[2][1] == original_formatter


def _log_one_logname(logname, level):
    """Log only once to logger associated with name ``logname``"""
    log = logging.getLogger(logname)
    log.log(level, 'into multiprocessing')


@parametrize('use_process', [False, True])
@parametrize('n_logs', [1, 2, 3])
def test_log_multiprocessing_initmain(qhandler, logger, logger_level,
                                      list_handler, use_process, n_logs):
    """Log from multiple processes to subprocess, handler initialised in main
    """
    logger.addHandler(qhandler[1])
    worker = phproc.get_worker(name=logger.name, multiprocessing=True)

    with phlog.SetupQueueListener(qhandler[0], handlers=[list_handler[0], ],
                                  use_process=use_process):
        for i in range(n_logs):
            worker(_log_one_logname, logger.name, logger_level+1)
        worker.get_results()
        worker.close()

    assert len(list_handler[1]) == n_logs
    for record in list_handler[1]:
        assert record.levelno > logger_level

"""Test pyhetdex.tools.logging_helper"""

import itertools as it
import logging
import multiprocessing
import os
import re

import nose.tools as nt

import settings

import pyhetdex.tools.logging_helper as phlog
import pyhetdex.tools.processes as phproc


_queue_loggers = {}


def setup_module(module):
    """nose fixture: setup the module variables"""
    module.logfile = os.path.join(settings.datadir, "queue.log")
    module.LEVEL = logging.DEBUG
    module.LEVELS = it.cycle([logging.CRITICAL, logging.ERROR, logging.WARNING,
                              logging.INFO, logging.DEBUG])
    module.n_levels = 5
    module.logmsg = ("What a piece of work is a man! How noble in reason, how"
                     " infinite in faculty, in form and moving how express and"
                     " admirable, in action how like an angel, in apprehension"
                     " how like a god -- the beauty of the world, the paragon"
                     " of animals!")
    module.n_logs = 10  # number of log messages
    pattern = r'\[\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2},\d{3}\]'
    pattern += r' \[(?:CRITICAL|ERROR|WARNING|INFO|DEBUG)\]'
    pattern += r' (?:' + module.logmsg + r')'
    module.pattern = re.compile(pattern)


def _filehandler(fname="", fmt="[%(asctime)s] [%(levelname)s] %(message)s",
                 level=None):
    """Return a file handler for the tests.

    Default to ``logfile`` if ``fname`` is an empty string

    Default to ``LEVEL`` if ``level`` is None
    """
    handler = logging.FileHandler(fname if fname else logfile)
    handler.setFormatter(logging.Formatter(fmt=fmt))
    handler.setLevel(level if level else LEVEL)

    return handler


def _make_logger(name, *handlers, **kwargs):
    """get the logger and add the handlers with

    Default to ``LEVEL`` if ``level`` is None
    """
    logger = logging.getLogger(name=name)
    logger.setLevel(kwargs.get('level', LEVEL))
    for h in handlers:
        logger.addHandler(h)
    return logger


def _init_queue_handler(name, queue_):
    """When logging with multiprocessors, the handler must be initialised on
    every process"""
    qhandler = phlog.QueueHandler(queue_)
    _make_logger(name, qhandler)


def _random_log(logger, nlogs=None):
    """Log ``nlogs`` times"""
    for i in range(nlogs if nlogs else n_logs):
        logger.log(next(LEVELS), logmsg)


def _log_one_logname(logname):
    """Log only once to logger associated with name ``logname``"""
    logger = logging.getLogger(logname)
    logger.log(next(LEVELS), logmsg)


def _compare_log_line(logfile):
    """Compare all the lines in the log file are as expected
    Returns a list of True or False whether the whole lines match or not
    """
    matched = []
    with open(logfile, mode='r') as f:
        for l in f:
            l = l.strip('\n')  # strip the new line
            match = pattern.match(l)
            if match is not None and match.endpos == len(l):
                matched.append(True)
            else:
                matched.append(False)
    return matched


def _compare_exception_log(logfile):
    """check that the last 5 are the correctly the exception
    """
    with open(logfile, mode='r') as f:
        last_lines = f.readlines()[-5:]

    nt.assert_in("CRITICAL", last_lines[0], msg="Not a critical log")
    nt.assert_in("Traceback (most recent call last):", last_lines[1],
                 msg="Not a traceback")
    nt.assert_regexp_matches(last_lines[2],
                             r"File .*?test_logging_helper\.py.*?, in"
                             r" test_log_setup_caught_exception")
    for ll in last_lines[-2:]:
        nt.assert_regexp_matches(ll, r"RuntimeError.*?test how __exit__ deal"
                                 r" with errors")


def teardown_func():
    """teardown function tests: remove the log file
    """
    os.remove(logfile)


@nt.with_setup(teardown=teardown_func)
def test_log_sp():
    """Test the QueueHandler and QueueListener in the same process
    """
    q = multiprocessing.Queue()
    qhandler = phlog.QueueHandler(q)

    logger = _make_logger("queue_thread", qhandler)

    with phlog.SetupQueueListener(q, handlers=[_filehandler()],
                                  use_process=False):
        _random_log(logger)

    q.close()

    # check that the number of log lines and the messages are correct
    matched = _compare_log_line(logfile)
    nt.assert_equal(len(matched), n_logs, msg="Wrong number of log lines")
    nt.assert_equal(sum(matched), n_logs, msg="Wrong number of matching log"
                    " lines")


@nt.with_setup(teardown=teardown_func)
def test_log_setup():
    """Test the SetupQueueListener in a separate process
    """
    q = multiprocessing.Queue()
    qhandler = phlog.QueueHandler(q)

    logger = _make_logger("queue_process", qhandler)

    with phlog.SetupQueueListener(q, handlers=[_filehandler()],
                                  use_process=True):
        _random_log(logger)

    q.close()

    # check that the number of log lines and the messages are correct
    matched = _compare_log_line(logfile)
    nt.assert_equal(len(matched), n_logs, msg="Wrong number of log lines")
    nt.assert_equal(sum(matched), n_logs, msg="Wrong number of matching log"
                    " lines")


@nt.with_setup(teardown=teardown_func)
@nt.raises(RuntimeError)
def test_log_setup_exception():
    """Test the SetupQueueListener with exceptions
    """
    q = multiprocessing.Queue()
    qhandler = phlog.QueueHandler(q)

    logger = _make_logger("raise_queue", qhandler)

    try:
        with phlog.SetupQueueListener(q, handlers=[_filehandler()]):
            _random_log(logger)
            raise RuntimeError("test how __exit__ deal with errors")
    finally:  # close anyway
        q.close()


@nt.with_setup(teardown=teardown_func)
def test_log_setup_caught_exception():
    """Test the SetupQueueListener with caught exception
    """
    q = multiprocessing.Queue()
    qhandler = phlog.QueueHandler(q)

    logger = _make_logger("catch_queue", qhandler)

    try:
        with phlog.SetupQueueListener(q, handlers=[_filehandler()]):
            _random_log(logger)
            raise RuntimeError("test how __exit__ deal with errors")
    except RuntimeError:
        pass
    finally:
        q.close()

    # check that the number of log lines and the messages are correct
    matched = _compare_log_line(logfile)
    nt.assert_equal(len(matched), n_logs+5, msg="Wrong number of log lines")
    nt.assert_equal(sum(matched), n_logs, msg="Wrong number of matching log"
                    " lines")
    _compare_exception_log(logfile)


@nt.with_setup(teardown=teardown_func)
def test_log_setup_level_respect():
    """Test the QueueListener in a separate process: respect handler level
    """
    q = multiprocessing.Queue()
    qhandler = phlog.QueueHandler(q)

    logger = _make_logger("queue_respect", qhandler)

    handler = _filehandler(level=logging.WARNING)
    with phlog.SetupQueueListener(q, handlers=[handler],
                                  use_process=True,
                                  respect_handler_level=True):
        _random_log(logger)

    q.close()

    # check that the number of log lines and the messages are correct
    matched = _compare_log_line(logfile)
    nt.assert_equal(len(matched), n_logs/5*3, msg="Wrong number of log lines")
    nt.assert_equal(sum(matched), n_logs/5*3, msg="Wrong number of matching"
                    " log lines")


@nt.with_setup(teardown=teardown_func)
def test_log_setup_nolevel_respect():
    """Test the QueueListener in a separate process: don't respect handler level
    """
    q = multiprocessing.Queue()
    qhandler = phlog.QueueHandler(q)

    logger = _make_logger("queue_norespect", qhandler)

    handler = _filehandler(level=logging.WARNING)
    with phlog.SetupQueueListener(q, handlers=[handler],
                                  use_process=True,
                                  respect_handler_level=False):
        _random_log(logger)

    q.close()

    # check that the number of log lines and the messages are correct
    matched = _compare_log_line(logfile)
    nt.assert_equal(len(matched), n_logs, msg="Wrong number of log lines")
    nt.assert_equal(sum(matched), n_logs, msg="Wrong number of matching log"
                    " lines")


@nt.with_setup(teardown=teardown_func)
def test_log_multiprocessing():
    """Test the logging from multiple processes to a subprocess
    """
    q = multiprocessing.Queue()
    logger_name = "queue_multiprocess"

    worker = phproc.get_worker(name="use_process", multiprocessing=True,
                               initializer=_init_queue_handler,
                               initargs=(logger_name, q))

    with phlog.SetupQueueListener(q, handlers=[_filehandler()],
                                  use_process=True):
        for i in range(n_logs):
            worker(_log_one_logname, logger_name)
        worker.get_results()
        worker.close()

    q.close()

    # check that the number of log lines and the messages are correct
    matched = _compare_log_line(logfile)
    nt.assert_equal(len(matched), n_logs, msg="Wrong number of log lines")
    nt.assert_equal(sum(matched), n_logs, msg="Wrong number of matching log"
                    " lines")


@nt.with_setup(teardown=teardown_func)
def test_log_multiprocessing_thread():
    """Test the logging from multiple processes to a thread
    """
    q = multiprocessing.Queue()
    logger_name = "queue_multiprocess_thread"

    worker = phproc.get_worker(name="use_thread", multiprocessing=True,
                               initializer=_init_queue_handler,
                               initargs=(logger_name, q))

    with phlog.SetupQueueListener(q, handlers=[_filehandler()],
                                  use_process=False):
        for i in range(n_logs):
            worker(_log_one_logname, logger_name)
        worker.get_results()
        worker.close()

    q.close()

    # check that the number of log lines and the messages are correct
    matched = _compare_log_line(logfile)
    nt.assert_equal(len(matched), n_logs, msg="Wrong number of log lines")
    nt.assert_equal(sum(matched), n_logs, msg="Wrong number of matching log"
                    " lines")

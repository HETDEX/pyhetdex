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
    # re match standard log formatting
    pattern_date = r'\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2},\d{3}'
    pattern_pid = r'\d{1,7}'
    pattern_level = r'(?:CRITICAL|ERROR|WARNING|INFO|DEBUG)'

    pattern = r'\[' + pattern_pid + r' - ' + pattern_date + r'\]'
    pattern += r' \[' + pattern_level + r'\] (?:' + module.logmsg + r')'
    module.pattern = re.compile(pattern)

    # formatter for the Logger adapter
    module.extras = {"custom": "custom key"}
    module.adapter_fmt = ("[%(custom)s - %(asctime)s] [%(levelname)s]"
                          " %(message)s")

    # re match adapter log formatting
    pattern = r'\[' + module.extras['custom'] + r' - ' + pattern_date + r'\]'
    pattern += r' \[' + pattern_level + r'\] (?:' + module.logmsg + r')'
    module.adapter_pattern = re.compile(pattern)


def _filehandler(fname="",
                 fmt="[%(process)d - %(asctime)s] [%(levelname)s] %(message)s",
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


def _compare_log_line(logfile, pattern_=None):
    """Compare all the lines in the log file are as expected
    Returns a list of True or False whether the whole lines match or not
    """
    matched = []
    pattern_ = pattern_ if pattern_ else pattern
    with open(logfile, mode='r') as f:
        for l in f:
            l = l.strip('\n')  # strip the new line
            match = pattern_.match(l)
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
    """QueueHandler and QueueListener in the same process
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
    """Use SetupQueueListener in a separate process
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
    """SetupQueueListener with exceptions
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
    """Catch the exception after exiting SetupQueueListener
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
    """QueueListener respecting the handler level
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
    """QueueListener not respecting the handler level
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
def test_log_multiprocessing_initmain():
    """Log from multiple processes to subprocess, handler initialised in main
    """
    q = multiprocessing.Queue()
    logger_name = "queue_multiprocess_initmain"

    _init_queue_handler(logger_name, q)

    worker = phproc.get_worker(name="use_process_initmain",
                               multiprocessing=True)

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
def test_log_multiprocessing():
    """Log from multiple processes to subprocess, handler initialised in worker
    """
    q = multiprocessing.Queue()
    logger_name = "queue_multiprocess_worker"

    worker = phproc.get_worker(name="use_process_worker", multiprocessing=True,
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
def test_log_multiprocessing_thread_initmain():
    """Log from multiple processes to a thread, handler initialised main
    """
    q = multiprocessing.Queue()
    logger_name = "queue_multiprocess_thread_initmain"

    _init_queue_handler(logger_name, q)

    worker = phproc.get_worker(name="use_thread_initmain",
                               multiprocessing=True)

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


@nt.with_setup(teardown=teardown_func)
def test_log_multiprocessing_thread():
    """Log from multiple processes to a thread, handler initialised in worker
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


@nt.with_setup(teardown=teardown_func)
def test_log_multiprocessing_and_main():
    """Log from main and child processes to a subprocess; initialised in main
    """
    q = multiprocessing.Queue()
    logger_name = "queue_main_multiprocess"

    # create the logger in the main process
    qhandler = phlog.QueueHandler(q)
    logger = _make_logger(logger_name, qhandler)

    # create the workers and the respective loggers
    worker = phproc.get_worker(name="mm_use_process", multiprocessing=True)

    with phlog.SetupQueueListener(q, handlers=[_filehandler()],
                                  use_process=True):
        _random_log(logger)  # log from the main process
        for i in range(n_logs):
            worker(_log_one_logname, logger_name)
        worker.get_results()
        worker.close()

    q.close()

    # check that the number of log lines and the messages are correct
    matched = _compare_log_line(logfile)
    nt.assert_equal(len(matched), 2*n_logs, msg="Wrong number of log lines")
    nt.assert_equal(sum(matched), 2*n_logs, msg="Wrong number of matching log"
                    " lines")


@nt.with_setup(teardown=teardown_func)
def test_log_adapter():
    """QueueHandler with logger adapter
    """
    q = multiprocessing.Queue()
    qhandler = phlog.QueueHandler(q)

    logger_ = _make_logger("logger_adapt", qhandler)

    logger = logging.LoggerAdapter(logger_, extras)

    with phlog.SetupQueueListener(q, handlers=[_filehandler(fmt=adapter_fmt)],
                                  use_process=False):
        _random_log(logger)

    q.close()

    # check that the number of log lines and the messages are correct
    matched = _compare_log_line(logfile, pattern_=adapter_pattern)
    nt.assert_equal(len(matched), n_logs, msg="Wrong number of log lines")
    nt.assert_equal(sum(matched), n_logs, msg="Wrong number of matching log"
                    " lines")

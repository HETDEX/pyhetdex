"""Test pyhetdex.tools.processes"""
from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

import multiprocessing.pool as mp
import time

import pytest

import pyhetdex.tools.processes as pr

parametrize = pytest.mark.parametrize
xfail_value_error = pytest.mark.xfail(raises=ValueError,
                                      reason="Single processor failing")
xfail_timeout = pytest.mark.xfail(raises=mp.TimeoutError,
                                  reason='Hit timeout')


def sleep(i):
    "function to execute"
    print("sleeping for", i)
    time.sleep(i/10.)
    print("awoken", i)
    return i


def fail(i):
    """Raise a ValueError"""
    raise ValueError(i)


def execute_sleep(worker):
    """run ``_foo`` 10 times"""
    for i in range(10):
        worker(sleep, i)

    # get the jobs and the results and check that they are correct
    jobs = worker.jobs
    results = worker.get_results()
    assert len(jobs) == 10
    assert len(jobs) == len(results)

    # check that the result is correct
    assert sorted(results) == list(range(10))

    # check that the job stats are correct
    stats = worker.jobs_stat()
    assert stats[0] == 10  # successful jobs
    assert stats[0] == stats[2]  # all successful
    assert stats[1] == 0  # no failures

    # clear and check it
    worker.clear_jobs()
    assert len(worker.jobs) == 0

    # close
    worker.close()


def execute_fail(worker):
    """run a function raising a value error 1 times, without catching the
    error"""

    worker(fail, 1)
    worker.get_results()
    worker.clear_jobs()
    worker.close()


def execute_fail_safe(worker):
    """run ``fail`` 10 times"""
    for i in range(10):
        worker(fail, i)

    # get the jobs and the results and check that they are correct
    jobs = worker.jobs
    results = worker.get_results(fail_safe=True)
    assert len(jobs) == 10
    assert len(jobs) == len(results)

    # check that the result is all "ValueError"
    assert sum(isinstance(i, ValueError) for i in results) == 10

    # check that the job stats are correct
    stats = worker.jobs_stat()
    assert stats[0] == 10  # finished
    assert stats[0] == stats[1]  # all failures
    assert stats[0] == stats[2]  # all finished

    # clear and check it
    worker.clear_jobs()
    assert len(worker.jobs) == 0

    # close
    worker.terminate()


params = parametrize('execute, name, multiprocessing, result_class',
                     [(execute_sleep, 'sp', False, pr.Result),
                      (execute_sleep, 'sp', False, pr.DeferredResult),
                      (execute_sleep, 'mp', True, None),
                      xfail_value_error((execute_fail, 'sp_f', False,
                                         pr.Result)),
                      xfail_value_error((execute_fail, 'sp_f', False,
                                         pr.DeferredResult)),
                      xfail_value_error((execute_fail, 'mp_f', True, None)),
                      (execute_fail_safe, 'sp_fs', False, pr.Result),
                      (execute_fail_safe, 'sp_fs', False, pr.DeferredResult),
                      (execute_fail_safe, 'mp_fs', True, None)])


@params
def test_processes(execute, name, multiprocessing, result_class):
    "Run the processes"
    try:
        execute(pr.get_worker(name=name, multiprocessing=multiprocessing,
                              result_class=result_class))
    finally:
        pr.remove_worker(name=name)


@params
def test_with(execute, name, multiprocessing, result_class):
    """with statement"""
    try:
        with pr.get_worker(name=name,
                           multiprocessing=multiprocessing,
                           result_class=result_class) as worker:
            execute(worker)
    finally:
        pr.remove_worker(name=name)


@pytest.mark.xfail(raises=pr.WorkerNameException,
                   reason='No worker with the given name created')
def test_remove_empty():
    """Try to remove a non existing worker"""
    pr.remove_worker(name='this_does_not_exist')


@parametrize('name, multiprocessing, pool',
             [('sa', False, type(None)), ('ma', True, mp.Pool)])
def test_worker_attributes(name, multiprocessing, pool):
    """Test the attributes"""
    try:
        with pr.get_worker(name=name,
                           multiprocessing=multiprocessing) as worker:
            assert worker.multiprocessing == multiprocessing
            assert isinstance(worker.pool, pool)
    finally:
        pr.remove_worker(name=name)


@parametrize('name, multiprocessing, timeout',
             [('nwm', True, None), ('wm', True, 5),
              xfail_timeout(('fwm', True, 0.5)),
              ('ws', False, None), ('ws', True, 5),
              ('ws', False, 0.5),
              ])
def test_wait(name, multiprocessing, timeout):
    """Wait for a while"""
    try:
        with pr.get_worker(name=name,
                           multiprocessing=multiprocessing) as worker:
            for i in range(10):
                worker(sleep, i)

            worker.wait(timeout)
            results = [j.get(0) for j in worker.jobs]
            assert len(results) == 10
    finally:
        pr.remove_worker(name=name)

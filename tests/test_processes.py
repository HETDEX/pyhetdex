"""Test pyhetdex.tools.processes"""

import time

import nose.tools as nt

import pyhetdex.tools.processes as pr


def _sleep(i):
    "function to execute"
    print("sleeping for", i)
    time.sleep(i/10.)
    print("awoken", i)
    return i


def _execute_sleep(worker):
    """run ``_foo`` 10 times"""
    for i in range(10):
        worker(_sleep, i)

    # get the jobs and the results and check that they are correct
    jobs = worker.jobs
    results = worker.get_results()
    nt.eq_(len(jobs), 10)
    nt.eq_(len(jobs), len(results))

    # check that the result is correct
    nt.eq_(sorted(results), list(range(10)))

    # check that the job stats are correct
    stats = worker.jobs_stat()
    nt.eq_(stats[0], 10)  # successful jobs
    nt.eq_(stats[0], stats[2])  # all successful
    nt.eq_(stats[1], 0)  # no failures

    # clear and check it
    worker.clear_jobs()
    nt.eq_(len(worker.jobs), 0)

    # close
    worker.close()


def test_single_processes():
    "single process, all success"
    _execute_sleep(pr.get_worker(name='sp'))


def test_multi_processes():
    "multi process, all success"
    _execute_sleep(pr.get_worker(name='mp', multiprocessing=True))


def _fail(i):
    """Raise a ValueError"""
    raise ValueError(i)


def _execute_fail(worker):
    """run ``_fail`` 1 times, without catching the error"""
    worker(_fail, 1)
    worker.get_results()
    worker.clear_jobs()
    worker.close()


@nt.raises(ValueError)
def test_single_processes_fail():
    "single process, fail"
    _execute_fail(pr.get_worker(name="sp_f"))


@nt.raises(ValueError)
def test_multi_processes_fail():
    "multi process, fail"
    _execute_fail(pr.get_worker(name="mp_f", multiprocessing=True))


def _execute_fail_safe(worker):
    """run ``_fail`` 10 times"""
    for i in range(10):
        worker(_fail, i)

    # get the jobs and the results and check that they are correct
    jobs = worker.jobs
    results = worker.get_results(fail_safe=True)
    nt.eq_(len(jobs), 10)
    nt.eq_(len(jobs), len(results))

    # check that the result is all "ValueError"
    nt.eq_(sum(isinstance(i, ValueError) for i in results), 10)

    # check that the job stats are correct
    stats = worker.jobs_stat()
    nt.eq_(stats[0], 10)  # finished
    nt.eq_(stats[0], stats[1])  # all failures
    nt.eq_(stats[0], stats[2])  # all finished

    # clear and check it
    worker.clear_jobs()
    nt.eq_(len(worker.jobs), 0)

    # close
    worker.terminate()


def test_single_processes_failsafe():
    "single process, catch failures"
    _execute_fail_safe(pr.get_worker(name="sp_fs"))


def test_multi_processes_failsafe():
    "multi process, catch failures"
    _execute_fail_safe(pr.get_worker(name="mp_fs", multiprocessing=True))


def test_with():
    """multiprocessing and with statement"""
    with pr.get_worker(name='with_success') as worker:
        for i in range(10):
            worker(_sleep, i)
    worker.clear_jobs()


@nt.raises(RuntimeError)
def test_with_fail():
    """multiprocessing and with statement with an error raise"""
    with pr.get_worker(name='with_success', multiprocessing=True) as worker:
        for i in range(10):
            worker(_sleep, i)
        raise RuntimeError("block computation")

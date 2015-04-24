"""Test pyhetdex.tools.processes"""

import time

import pyhetdex.tools.processes as pr


def _foo(i):
    "function to execute"
    print("sleeping for", i)
    time.sleep(i/10.)
    print("awoken", i)


def test_single_processes():
    "single process"
    worker = pr.get_worker(name='sp')
    for i in range(10):
        worker(_foo, i)


def test_multi_processes():
    "multi process"
    worker = pr.get_worker(name='mp', multiprocessing=True)
    jobs = [worker(_foo, i) for i in range(10)]
    for j in jobs:
        j.get()

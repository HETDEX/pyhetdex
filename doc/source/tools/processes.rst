.. :py:currentmodule:: pyhetdex.tools.processes

:py:mod:`processes` -- Single/Multiprocessing abstraction
*********************************************************

.. automodule:: pyhetdex.tools.processes

Examples
========

.. doctest::

    >>> import pyhetdex.tools.processes as p
    >>> def func(args):
    ...     print(", ".join(args))
    ...     return " ".join(args)

Run single processor jobs

.. doctest::

    >>> worker_sp = p.get_worker(name="singlep")
    >>> job = worker_sp(func, ["from", "single", "processor"])
    from, single, processor
    >>> job
    <pyhetdex.tools.processes.Result object at ...>
    >>> job.get()
    'from single processor'
    >>> worker_sp.get_results()
    ['from single processor']
    >>> worker_sp.close()

Or multiprocessor jobs

.. doctest::

    >>> worker_mp = p.get_worker(name="multip", multiprocessing=True)
    >>> job = worker_mp(func, ["from", "multi", "processor"])
    >>> job
    <multiprocessing.pool.ApplyResult object at ...>
    >>> job.get()  # doctest: +SKIP
    'from single processor'
    >>> worker_mp.get_results()  # doctest: +SKIP
    ['from multi processor']
    >>> worker_mp.close()

Run some initialisation function when creating the multiprocessing pool

.. doctest::

    >>> def init_func(message):
    ...     print(message)
    >>> worker_mp_init = p.get_worker(name="multip_init", multiprocessing=True,
    ...                               initializer=init_func,
    ...                               initargs=("docstring",))
    >>> worker_mp_init.close()

Alternatively, you can use the worker within a :keyword:`with` statement

.. doctest::
    
    >>> def func1(args):
    ...     return " ".join(args[::-1])
    >>> with p.get_worker(name="inwith", multiprocessing=True) as wworker:
    ...     wworker(func1, ["in", "with", "statement"])
    ...     wworker.get_results()  # doctest: +SKIP
    ['in with statement']

Public inteface
===============

.. autofunction:: pyhetdex.tools.processes.get_worker
.. autofunction:: pyhetdex.tools.processes.remove_worker
.. autofunction:: pyhetdex.tools.processes.ignore_keyboard_interrupt

Exceptions
==========

.. autoexception:: pyhetdex.tools.processes.WorkerException
   :show-inheritance:

.. autoexception:: pyhetdex.tools.processes.WorkerNameException
   :show-inheritance:

Implementation
==============

Worker implementations
----------------------

Although the class itself should be considered as private, the attributes and
method listed below are public

.. autoclass:: pyhetdex.tools.processes._Worker
   :members:
   :special-members: __call__, __enter__

Result class
------------

.. autoclass:: pyhetdex.tools.processes.Result
   :members:

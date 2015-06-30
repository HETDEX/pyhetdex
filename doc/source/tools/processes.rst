.. :py:currentmodule:: pyhetdex.tools.processes

:py:mod:`processes` -- Single/Multiprocessing abstraction
*********************************************************

.. automodule:: pyhetdex.tools.processes

Examples
========

.. testsetup:: *

    import pyhetdex.tools.processes as p

Create a single or a multiprocessing worker

.. doctest::

    >>> worker_sp = p.get_worker(name="singlep")
    >>> worker_mp = p.get_worker(name="multip", multiprocessing=True)

Execute a function when initialising a multiprocessing worker

.. doctest::

    >>> def init_func(message):
    ...     print(message)
    >>> worker_mp_init = p.get_worker(name="multip", multiprocessing=True,
    ...                               initializer=init_func,
    ...                               initargs=("docstring"))

Execute a function by one of the workers

.. doctest::

    >>> def func(args):
    ...     print(", ".join(args))
    ...     return " ".join(args)
    >>> job = worker_sp(func, ["from", "single", "processor"])
    from, single, processor
    >>> job  # docstring: +ELLIPSES
    <pyhetdex.tools.processes.Result object at ...>
    >>> job = worker_mp(func, ["from", "multi", "processor"])
    >>> job  # docstring: +ELLIPSES
    <multiprocessing.pool.ApplyResult object at ...>

Get the results

.. doctest::

    >>> worker_sp.get_results()
    ['from single processor']
    >>> worker_mp.get_results()  # doctest: +SKIP
    ['from multi processor']

Close the workers, does nothing for single processor workers
    
.. doctest::

    >>> worker_sp.close()
    >>> worker_mp.close()
    >>> worker_mp_init.close()

Public inteface
===============

.. autofunction:: pyhetdex.tools.processes.get_worker
.. autofunction:: pyhetdex.tools.processes.ignore_keyboard_interrupt

Implementation
==============

Worker implementations
----------------------

Although the class itself should be considered as private, the attributes and
method listed below are public

.. autoclass:: pyhetdex.tools.processes._Worker
   :members:
   :special-members: __call__

Result class
------------

.. autoclass:: pyhetdex.tools.processes.Result
   :members:

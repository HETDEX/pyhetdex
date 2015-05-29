.. :py:currentmodule:: pyhetdex.tools

:py:mod:`tools.processes` -- Single/Multiprocessing abstraction
***************************************************************

.. automodule:: pyhetdex.tools.processes

Public inteface
===============

.. autofunction:: pyhetdex.tools.processes.get_worker
.. autofunction:: pyhetdex.tools.processes.ignore_keyboard_interrupt

.. autoclass:: pyhetdex.tools.processes.Result
   :members:


Implementation
==============

Although the class itself should be considered as private, the attributes and
method listed below are public

.. autoclass:: pyhetdex.tools.processes._Worker
   :members:
   :special-members: __call__

.. :py:currentmodule:: pyhetdex.het.fplane

:py:mod:`fplane` -- Focal plane
*******************************

.. automodule:: pyhetdex.het.fplane

Use
===

.. testsetup:: *

    from pyhetdex.het.fplane import IFU, FPlane

The simplest use is to create a ``fplane`` instance passing the name of the
focal plane file:

>>> fplane = FPlane("fplane.txt")  # doctest: +SKIP
>>> print(fplane.difus)  # doctest: +SKIP
{'001': <pyhetdex.het.fplane.IFU object at 0x7ff6a493c1d0>,
 '002': <pyhetdex.het.fplane.IFU object at 0x7ff6a493d1d0>, ...}

IFU Customisation
-----------------

If you need to customise the :class:`IFU` object, without changing the constructor
signature, you can do something like this:

.. doctest::

    >>> class MyIFU(IFU):
    ...     def __init__(self, ifuslot, x, y, specid, specslot,
    ...                  ifuid, ifurot, platescl):
    ...         super(MyIFU, self).__init__(self, ifuslot, x, y, specid,
    ...                                     specslot, ifuid, ifurot, platescl)
    ...         # do something else
    ...     def new_method(self, a_variable):
    ...         # implement
    ...         pass
    >>> fplane = FPlane("fplane.txt", ifu_class=MyIFU)  # doctest: +SKIP

FPlane customisation
--------------------

For more complex customisations, when you use a different way of storing
the IFU informations, e.g. a ``list``, a different ``__init__`` signature,
..., you can override the :meth:`FPlane.add_ifu` method:

.. doctest::

    >>> class MyFPlane(FPlane):
    ...     def add_ifu(self, line):
    ...         # reimplement at need
    ...         pass

Implementation
==============

.. autoclass:: pyhetdex.het.fplane.IFU
   :members:
   :undoc-members:
   :private-members:

.. autoclass:: pyhetdex.het.fplane.FPlane
   :members:
   :undoc-members:
   :private-members:
   :exclude-members: ihmpids, by_ihmpid 

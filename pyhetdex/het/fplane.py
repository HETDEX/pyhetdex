"""Base class for fplane file parsing and IFU.

This module provides a basic parser for the focal plane file and an object
containing the informations about the IFU from the focal plane.

The focal plane is expected to be::

    ##IFUID x["]   y["] xpos ypos specid
    001 -450.0  150.0 1 3 001
    002 -450.0   50.0 1 4 002

Commented lines are ignored.
"""
from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

import six


class NoIFUError(KeyError):
    """Error raised when the required ifu does not exists"""
    pass


class UnknownIDTypeError(ValueError):
    """Unknown id type"""
    pass


class IFU(object):
    """Contain the information for the IFU from the focal plane file.

    Parameters
    ----------
    ifuid : string
        id of the ifu
    x, y : string or float
        x and y position of the ifu in the focal plane
    xid, yid : string or int
        x (column) and y (row) id of the ifu in the ifu head mounting plate
        (IHMP)
    specid : string
        id of the spectrograph where the ifu is plugged into

    Attributes
    ----------
    ifuid, x, y, xid, yid, specid : as before
    ihmpid : string
        id of the IHMP seat address
    """
    def __init__(self, ifuid, x, y, xid, yid, specid):
        self.ifuid = ifuid
        self.x = float(x)
        self.y = float(y)
        self.xid = int(xid)
        self.yid = int(yid)
        self.specid = specid
        self.ihmpid = "{0:02d}{1:01d}".format(self.xid, self.yid)

    def __str__(self):
        msg = "ifu: '{0}'; IHMP: '{1}'; spectrograph: '{2}'"
        return msg.format(self.ifuid, self.ihmpid, self.specid)


class FPlane(object):
    """Focal plane.

    Contains the dictionary of :class:`IFU` instance (or derived or others),
    with the ifu id as key.

    Parameters
    ----------
    fplane_file : string
        name of the file containing the ids and position of the IFUs
    ifu_class : :class:`IFU` instance (or anything else)
        class definition containing the IFU information.

    Attributes
    ----------
    ifus
    difus
    ifuids
    ihmpids
    specids
    """
    def __init__(self, fplane_file, ifu_class=IFU):
        self._fplane_file = fplane_file
        self._IFU = ifu_class
        self._ifus_by_id = {}
        self._ifus_by_ihmp = {}
        self._ifus_by_spec = {}

        self._load_fplane(fplane_file)

    @property
    def ifus(self):
        """list of :class:`IFU` instances"""
        return self._ifus_by_id.values()

    @property
    def ids(self):
        """list of ifu ids

        Deprecated
        """
        import warnings
        with warnings.catch_warnings():
            warnings.simplefilter("default")
            warnings.warn("``ids`` is deprecated, please use ``ifuids``"
                          " instead", DeprecationWarning)
        return self._ifus_by_id.keys()

    @property
    def ifuids(self):
        """list of ifu ids"""
        return self._ifus_by_id.keys()

    @property
    def ihmpids(self):
        """list of ihmp ids"""
        return self._ifus_by_ihmp.keys()

    @property
    def specids(self):
        """list of spec ids"""
        return self._ifus_by_spec.keys()

    @property
    def difus(self):
        """dictionary of ifus; key: ifuid; value: :class:`IFU` instance"""
        return self._ifus_by_id

    def by_ifuid(self, ifuid):
        """Returns the ifu with ``ifuid``

        Parameters
        ----------
        ifuid : string
            id of the ifu

        Returns
        -------
        :class:`IFU` instance
        """
        try:
            return self._ifus_by_id[ifuid]
        except KeyError as e:
            six.raise_from(NoIFUError(e), e)

    def by_ihmpid(self, ihmpid):
        """Returns the ifu with ``ihmpid``

        Parameters
        ----------
        ihmpid : string
            id of the ihmp seat

        Returns
        -------
        :class:`IFU` instance
        """
        try:
            return self._ifus_by_ihmp[ihmpid]
        except KeyError as e:
            six.raise_from(NoIFUError(e), e)

    def by_specid(self, specid):
        """Returns the ifu with ``specid``

        Parameters
        ----------
        specid : string
            id of the spectrograph

        Returns
        -------
        :class:`IFU` instance
        """
        try:
            return self._ifus_by_spec[specid]
        except KeyError as e:
            six.raise_from(NoIFUError(e), e)

    def by_id(self, id_, idtype):
        """Returns the ifu with ``id_``

        Parameters
        ----------
        id_ : string
            id of the spectrograph
        idtype : str
            type of the id; must be one of 'ifuid', 'ihmpid', 'specid'

        Returns
        -------
        :class:`IFU` instance
        """
        if idtype == 'ifuid':
            ifu = self.by_ifuid
        elif idtype == 'ihmpid':
            ifu = self.by_ihmpid
        elif idtype == 'specid':
            ifu = self.by_specid
        else:
            raise UnknownIDTypeError("Id type {} is not known")

        return ifu(id_)

    def _load_fplane(self, fname):
        """Load the focal plane file and creates the :class:`IFU` instances

        Parameters
        ----------
        fname : string
            name of the focal plane file
        """
        with open(fname, mode='r') as f:
            for l in f:
                if l.startswith("#"):
                    continue
                self.add_ifu(l.strip("\n").strip())

    def add_ifu(self, line):
        """Parse a fplane ``line`` and add the IFU to the internal dictionary.

        Make sure that the ifuid, specid are a three digit string. Override
        this method if the ``ifu`` class constructor is not as the one of
        :class:`IFU`.

        Parameters
        ----------
        line : string
            line of the fplane file
        """
        ifuid, x, y, xid, yid, specid = [i.strip() for i in line.split()]
        ifuid = "{0:03d}".format(int(ifuid))
        specid = "{0:03d}".format(int(specid))
        _ifu = self._IFU(ifuid, x, y, xid, yid, specid)
        self._ifus_by_id[ifuid] = _ifu
        self._ifus_by_ihmp[_ifu.ihmpid] = _ifu
        self._ifus_by_spec[specid] = _ifu

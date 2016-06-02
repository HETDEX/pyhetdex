"""Base class for fplane file parsing and IFU.

This module provides a basic parser for the focal plane file and an object
containing the informations about the IFU from the focal plane.

The focal plane is expected to be::

    ##IFUSLOT X_FP   Y_FP   SPECID SPECSLOT IFUID IFUROT PLATESC
      001     -450.0 150.0  37     42       024   0.0    1.00

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
    ifuslot : string
        id of the ifu
    x, y : float
        x and y position of the ifu in the focal plane
    specid : int
        id of the spectrograph where the ifu is plugged into
    specslot : int
        id of the spectrograph slot where the spectrograph is plugged into
    ifuid : string
        id of the virus ifu bundle
    ifurot : float
        rotation of the IFU in its seat in the IHMP
    platescl : float
        focal plane plate scale at the position in the IHMP

    Attributes
    ----------
    ifuid, x, y, xid, yspecid : as before
    xid, yid : string or int
        x (column) and y (row) id of the ifu in the ifu head mounting plate
        (IHMP), generated from the ifuslot
    """
    def __init__(self, ifuslot, x, y, specid, specslot,
                 ifuid, ifurot, platescl):
        if type(ifuslot) is not str and type(ifuslot) is not unicode:
            raise TypeError('ifuslot must be string, not', type(ifuslot))
        self.ifuslot = ifuslot
        self.x = float(x)
        self.y = float(y)
        self.specid = int(specid)
        self.specslot = int(specslot)
        self.ifuid = ifuid
        self.ifurot = float(ifurot)
        self.platescl = float(platescl)
        self.xid = int(self.ifuslot[0:2])
        self.yid = int(self.ifuslot[2])

    def __str__(self):
        msg = "ifuslot: '{0}'; ifuid: '{1}'; specid: '{2}'"
        return msg.format(self.ifuslot, self.ifuid, self.specid)


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
        self._ifus_by_slot = {}
        self._ifus_by_spec = {}

        self._load_fplane(fplane_file)

    @property
    def ifus(self):
        """list of :class:`IFU` instances"""
        return self._ifus_by_id.values()

    @property
    def ifuids(self):
        """list of ifu ids"""
        return self._ifus_by_id.keys()

    @property
    def ifuslots(self):
        """list of ihmp ids"""
        return self._ifus_by_slot.keys()

    @property
    def ihmpids(self):
        """list of ifu ids

        Deprecated
        """
        import warnings
        with warnings.catch_warnings():
            warnings.simplefilter("default")
            warnings.warn("``ihmpids`` is deprecated, please use ``ifuslots``"
                          " instead", DeprecationWarning)
        return self._ifus_by_slot.keys()

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

    def by_ifuslot(self, ifuslot):
        """Returns the ifu with ``ifuslot``

        Parameters
        ----------
        ifuslot : string
            id of the ihmp slot

        Returns
        -------
        :class:`IFU` instance
        """
        try:
            return self._ifus_by_slot[ifuslot]
        except KeyError as e:
            six.raise_from(NoIFUError(e), e)

    def by_slotpos(self, x, y):
        """Returns the ifu in ifu slot position x, y

        Parameters
        ----------
        x : int
            x position in the IHMP (1 to 10)
        y : int
            y position in the IHMP (1 to 9)

        Returns
        -------
        :class:`IFU` instance
        """
        try:
            return self._ifus_by_slot['{:02d}{:d}'.format(x, y)]
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

        Deprecated
        """
        import warnings
        with warnings.catch_warnings():
            warnings.simplefilter("default")
            warnings.warn("``ihmpids`` is deprecated, please use ``ifuslots``"
                          " instead", DeprecationWarning)
        try:
            return self._ifus_by_slot[ihmpid]
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
        elif idtype == 'ifuslot':
            ifu = self.by_ifuslot
        elif idtype == 'ihmpid':
            import warnings
            with warnings.catch_warnings():
                warnings.simplefilter("default")
                warnings.warn("``ihmpid`` is deprecated, please use "
                              "``ifuslot`` instead", DeprecationWarning)
            ifu = self.by_ifuslot
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
        missing = 1
        with open(fname, mode='r') as f:
            for l in f:
                if l.startswith("#"):
                    continue
                line = l.strip("\n").strip()
                params = [i.strip() for i in line.split()]

                if params[5] == '000':
                    params[5] = 'N%02d' % missing
                    params[3] = '-%02d' % missing
                    missing += 1
                self.add_ifu(params)

    def add_ifu(self, fpars):
        """Parse a fplane ``line`` and add the IFU to the internal dictionary.

        Make sure that the ifuid, specid are a three digit string. Override
        this method if the ``ifu`` class constructor is not as the one of
        :class:`IFU`.

        Parameters
        ----------
        line : string
            line of the fplane file
        """
        ifuslot, x, y, specid, speclot, ifuid, ifurot, platescl = fpars
        _ifu = self._IFU(ifuslot, x, y, specid, speclot,
                         ifuid, ifurot, platescl)

        self._ifus_by_id[_ifu.ifuid] = _ifu
        self._ifus_by_slot[_ifu.ifuslot] = _ifu
        self._ifus_by_spec[_ifu.specid] = _ifu

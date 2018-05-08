# Misc python library to support HETDEX software and data analysis
# Copyright (C) 2015, 2016, 2017  "The HETDEX collaboration"
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.
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

    The input type are cast to the corresponding types when initialising the
    object.

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
    ifuid, x, y, specid, specslot, ifuid, ifurot, platescl : as before
    xid, yid : int
        x (column) and y (row) id of the ifu in the ifu head mounting plate
        (IHMP), generated from the ifuslot

    Raises
    ------
    TypeError
        if the ``ifuslot`` is not a string
    """
    def __init__(self, ifuslot, x, y, specid, specslot,
                 ifuid, ifurot, platescl):
        if not isinstance(ifuslot, six.string_types):
            raise TypeError('ifuslot must be string, not', type(ifuslot))
        self.ifuslot = ifuslot
        self.x = float(x)
        self.y = float(y)
        self.specid = int(specid)
        self.specslot = int(specslot)
        self.ifuid = str(ifuid)
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
    ifu_class : :class:`IFU` instance (or anything else), optional
        class definition containing the IFU information.
    empty_specid, empty_ifuid : string, optional
        if the entries for the SPECID (fourth column) or IFUID (sixt column)
        are as specified, they are replaced by a two digit negative number or a
        two digit number following a 'N'. The number is increased any time one
        of the two conditions is met. Use it with caution as the SPECID and
        IFUID are used as dictionary keywords and should not be duplicated to
        avoid losing IFUs
    exclude_ifuslot : list of string, optional
        list of ifu slot ids to exclude when loading the fplane file. The ids
        must much exactly the string in the first column of the file
    skip_empty : bool, optional
        if ``True`` skip one ifu if the specid/ifuid is marked as empty

    Attributes
    ----------
    ifus
    ifuids
    ifuslots
    specids
    difus_ifuid
    difus_ifuslot
    difus_specid
    """
    def __init__(self, fplane_file, ifu_class=IFU, empty_specid='00',
                 empty_ifuid='000', exclude_ifuslot=[], skip_empty=False):
        self._fplane_file = fplane_file
        self._IFU = ifu_class
        self._ifus_by_id = {}
        self._ifus_by_slot = {}
        self._ifus_by_spec = {}

        self._load_fplane(fplane_file, empty_specid, empty_ifuid,
                          exclude_ifuslot, skip_empty)

    @property
    def ifus(self):
        """list of :class:`IFU` instances"""
        return list(self._ifus_by_id.values())

    @property
    def ifuids(self):
        """list of IFUIDs (strings)"""
        return list(self._ifus_by_id.keys())

    @property
    def ifuslots(self):
        """list of IFUSLOTs (strings)"""
        return list(self._ifus_by_slot.keys())

    @property
    def specids(self):
        """list of SPECIDs (integers)"""
        return list(self._ifus_by_spec.keys())

    @property
    def difus_ifuid(self):
        """dictionary of ifus; key: IFUID (string); value: :class:`IFU`
        instance"""
        return self._ifus_by_id

    @property
    def difus_ifuslot(self):
        """dictionary of ifus; key: IFUSLOT (string); value: :class:`IFU`
        instance"""
        return self._ifus_by_slot

    @property
    def difus_specid(self):
        """dictionary of ifus; key: SPECID (int); value: :class:`IFU`
        instance"""
        return self._ifus_by_spec

    def by_ifuid(self, ifuid):
        """Returns the ifu with ``ifuid``

        Parameters
        ----------
        ifuid : string
            id of the ifu

        Returns
        -------
        :class:`IFU` instance

        Raises
        ------
        NoIFUError
            if there is no IFU identified by the input ID
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

        Raises
        ------
        NoIFUError
            if there is no IFU identified by the input ID
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

        Raises
        ------
        NoIFUError
            if there is no IFU for the input positions
        """
        try:
            return self._ifus_by_slot['{:02d}{:d}'.format(x, y)]
        except KeyError as e:
            six.raise_from(NoIFUError(e), e)

    def by_specid(self, specid):
        """Returns the ifu with ``specid``

        Parameters
        ----------
        specid : int or string
            id of the spectrograph; the value is cast to an integer

        Returns
        -------
        :class:`IFU` instance

        Raises
        ------
        NoIFUError
            if there is no IFU identified by the input ID
        TypeError
            if the input is not an int or a string that can be cast to an int
        """
        if isinstance(specid, six.string_types):
            try:
                specid = int(specid)
            except ValueError as e:
                msg = ('If specid is a string it must be a valid literal for'
                       ' int(), not ')
                six.raise_from(TypeError(msg, specid), e)
        elif isinstance(specid, (int, six.string_types)):
            pass
        else:
            raise TypeError('specid must be an integer or a string, not',
                            type(specid))

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
            type of the id; must be one of 'ifuid', 'ifuslot', 'specid'

        Returns
        -------
        :class:`IFU` instance

        Raises
        ------
        NoIFUError
            if there is no IFU identified by the input ID
        UnknownIDTypeError
            if the ID type is not known
        """
        if idtype == 'ifuid':
            ifu = self.by_ifuid
        elif idtype == 'ifuslot':
            ifu = self.by_ifuslot
        elif idtype == 'specid':
            ifu = self.by_specid
        else:
            raise UnknownIDTypeError("Id type {} is not known")

        return ifu(id_)

    def _load_fplane(self, fname, empty_specid, empty_ifuid, exclude_ifuslot,
                     skip_empty):
        """Load the focal plane file and creates the :class:`IFU` instances

        Parameters
        ----------
        fname : string
            name of the focal plane file
        empty_specid, empty_ifuid, exclude_ifuslot, skip_empty :
            see :class:`FPlane`
        """
        missing = 1
        with open(fname, mode='r') as f:
            for l in f:
                if l.startswith("#"):
                    continue
                line = l.strip("\n").strip()
                params = [i.strip() for i in line.split()]

                if params[0] in exclude_ifuslot:
                    continue

                changed = False
                if params[3] == empty_specid:
                    params[3] = '-%02d' % missing
                    changed = True
                    if skip_empty:
                        continue
                if params[5] == empty_ifuid:
                    params[5] = 'N%02d' % missing
                    changed = True
                    if skip_empty:
                        continue
                if changed:
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

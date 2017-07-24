# ``pyhetdex`` release notes

## Development version @ trunk

* Remove modules deprecated in v0.10.0 (issues #1641, #1676, #1677, #1349)
* pyhetdex.coordinates.astrometry: add option to use the IFUCen file (issue
  #1962) and to pass dither offsets (issue #1968)
* use ``configparser`` package in python 2 to backport python 3 implementation
  (issue #1979)
* move some functionality to get files from a distribution and copy them from
  VDAT (issue #1963)
* added --rhozp option to astrometry rotuines, to allow user to specify
  the rotation angle of the rho stage 
* Add pyhetdex.tools.db_helpers (from VDAT, issue #2026)

## Development version @ branches/selection_function_devel

* Changes to the selection function model
* Modified code to read in three fiber-extracted noise files, rather
  than a datacube

## Version 0.11.0

* Added routine to create an overview plot for one exposure
* Override configurations from the, e.g., the command line (issue #1849)
* Added tool to generate masks, i.e. corners of each IFU in
  a focal plane for a list of shots (issue #1873)

## Version 0.10.0

* pyhetdex.ltl.chebyshev: added; matrixCheby2D_7 function added (gregz)
* Made modifications to add_ra_dec based on Karl/Greg's feedback
* Added xy_to_ra_dec function that reads in-IFU positions and returns ra, dec
* pyhetdex.tools.configuration: ConfigParse.{get_list,get_list_of_list}: don't
  cast forcefully anymore (issue #1620, #1621). Not backward compatible
* copy tangent_projection_astropy into tangent_projection (#1636)
* deprecate some module and mark others as not tested/possibly changing (#1637)
* fplane parser: skip IFU by SLOTID (issue #1617) or when the SPECID/IFUID is
  marked as empty (issue #1618)
* fplane parser: fix properties according to their documentation (issue #1640)
* fix case when DITHER header key is not present or not set (issue #1674)
* cast list index to integer to comply with numpy >=1.12 (issue #1769)

## Version 0.9.0

* pyhetdex.cure.distortion: Added write routine and tests
* pyhetdex.cure.fibermodel: Added interpolation routines
* pyhetdex.cure.fiber_fractions: Computes the fill factor of 
  apertures by fibers, expected to be useful in any model of
  how likely you are to detect and LAE
* pyhetdex.coordinates.astrometry: Command line tools to add
  ra, dec to catalogues from VIRUS. Also a tool to add a 2D WCS
  to datacubes/apimages, but this is still a work in progress.
* pyhetdex.het.telescope: update the Shot class according to issue #1515; remove
  the illumination and image quality servers as they are not used
* pyhetdex.het.dither: pass the dither positions or a file with them from the
  command line (issue #1544)
* pyhetdex.het.dither: add the possibility to use the hetpupil executable when
  creating dither files

## Version 0.8.0

* pyhetdex.cure.distortion: make Distortion class compatible with
  multiple file versions. Supports version 14 and 17
* pyhetdex.cure.fibermodel: make FiberModel class compatible with
  multiple file versions. Supports version 16 to 21
* pyhetdex.cure.psfmodel: make PSFModel class compatible with
  multiple file versions. Supports version 2 and 3.
* update fplane file to new format (issue #1460)
* fix bug with distance calculation

## Version 0.7.0

* pyhetdex.het.reconstruct_ifu.QuickReconstructedIFU: change interface to ease
  reconstructing science images in VDAT. WARNING: non backward compatible change

## Version 0.6.0

* Deprecate pyhetdex.doc.sphinxext.todo; use the version shipped with
  sphinx>=1.4 in the module sphinx.ext.todo
* Processes: add DeferredResult class for defer function
  execution when running single processor jobs and allow to pass it to the
  ``_Worker`` object

## Version 0.5.0

* First version of tools to generate random catalogues; work in progress
* tools.processes: added function to remove a worker from the internal 
storage. Useful for instance to clear closed/terminated workers
* het.dither: executable dither_file improved and adapted for use with the 
output of ccdcombine

## Version 0.4.0

* pyhetdex.tools.configuration: more functionalities backported from python 3.4
  to python 2.7
* pyhetdex.tools.files.file_tools: better error messages when compiling regex
* documentation: add the version of pyhetdex

## Version 0.3.0

* First version released on a pypi-like server

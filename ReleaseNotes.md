
# ``pyhetdex`` release notes

## Development version @ trunk

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

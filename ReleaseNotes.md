# ``pyhetdex`` release notes

## Development version

* Deprecate pyhetdex.doc.sphinxext.todo; use the version shipped with
    sphinx>=1.4 in the module sphinx.ext.todo

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

#pyhetdex

`pyhetdex` is a python library designed to collect code can could be used by
different project like
[`Quicklook`](https://luna.mpe.mpg.de/wikihetdex/index.php/Quicklook),
[`simhetdex`](https://luna.mpe.mpg.de/wikihetdex/index.php/VIRUS_Data_Simulation_Framework)
or
[`Cure-WISE`](https://luna.mpe.mpg.de/wikihetdex/index.php/Overview_of_Cure-WISE).

## Installation

The code can be obtained from the svn repository using the following
command (this step is not necessary if the option `4` below is used)

    svn checkout svn://luna.mpe.mpg.de/pyhetdex/trunk

To use the library there you can use one of the following options (options 2, 3
and 4 install the library in locations already within the python path):

1. add `pyhetdex` to the python path. E.g. in bash:

        export PYTHONPATH=/path/to/pyhetdex:$PYTHONPATH

2. install the package with:

        python setup.py build
        python setup.py install
  or, to install it into `$HOME/.local/lib/pythonX.X/site-packages`

        python setup.py install --user

3. install using [`pip`](https://pip.pypa.io/en/latest/). This has the advantage
  that will pull and install all the [dependencies](#Dependencies) if they are not
  already present on the system.

        pip install /path/to/pyhetdex
  Add the `--user` option to install in the user `site-packages` directory

4. It is also possible to install `pyhetdex` directly from the svn repository,
without the need to download it first:

        pip install [--user] svn+svn://luna.mpe.mpg.de/pyhetdex/trunk

A note of `pip`: installing `numpy` and `scipy` at the same time can fail. If
during the installation you get the following error:

    File "/tmp/pip-build-K_FfsK/scipy/setup.py", line 237, in setup_package

        from numpy.distutils.core import setup

    ImportError: No module named numpy.distutils.core

    ----------------------------------------
    Command "/path/to/pythonX.X -c "import setuptools, tokenize; [omissis]
    failed with error code 1 in /tmp/pip-build-K_FfsK/scipy
install first `numpy` then `pyhetdex`

    pip install [--user] numpy

###Setuptools Configuration
Each of the subcommands in `python setup.py` can be configured either through a
`setup.cfg` file or through command line arguments. The latter overrides the
settings in the `setup.cfg` file. For more information check to [official
documentation](https://docs.python.org/2/distutils/configfile.html)

##Dependencies

Mandatory

    numpy
    scipy
    astropy

Optional:

    test: nose
          coverage
    documentation: sphinx
                   numpydoc

NOTE: as `pyfits` has been integrated into `astropy` and going out of support
and since the latter provides much more functionalities that the former, we do
not support pyfits.

##Development
If you are developing the library, consider it's possible to use the `develop`
command

    python setup.py develop

Instead of copying `pyhetdex` to the `site-packages` directory (as `install`
does) it will create a link pointing to the `pyhetdex` repository. This allow
you to modify the code and to test the changes without any need to reinstall the
library.
The command comes also with a `--uninstall` option that removes the link.
(sources:
[stackoverflow](http://stackoverflow.com/questions/19048732/python-setup-py-develop-vs-install),
[a blog](http://www.siafoo.net/article/77#id10))

###Testing

The tests are run using the [`nose`](https://nose.readthedocs.org/en/latest/)
framework. To run the tests execute

    python setup.py nosetests

If you also have installed the
[`coverage`](http://nedbatchelder.com/code/coverage/) package, a coverage test
will be run and a html report will be created. The report can be accessed
opening the file `cover/index.html` in any browser.

To any new functionality added to the library the appropriate number of tests
should be added. 

Good practice: any time the code is changed the tests should be run to check
that nothing has been broken and that we can recover the same results as before
(unless there was a bug, of course). The developer should commit after all the
tests succeed.

##Documentation

To build the documentation just go into the `doc` directory and run `make html`
or `make latex` there.

Every public function, method and class should be documented. Keeping also
private functions documented helps future development. The documentation must
be written following the [numpy
guidelines](https://github.com/numpy/numpy/blob/master/doc/HOWTO_DOCUMENT.rst.txt#id12).
The online documentation is then extracted using `sphinx` and the `numpydoc`
plugin.

When writing (28.01.2015) the modules `pyhetdex.astrometry.astrometry` and
`pyhetdex.het.ifu_centers` are appropriately documented to comply to the
standard. Other modules with follow.

##Notes

Please use [markdown](http://daringfireball.net/projects/markdown/syntax) syntax
so it can be easily converted to html or wiki format if needed **and** remains
very readable


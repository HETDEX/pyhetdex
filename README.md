#pyhetdex

This is the readme file of `pyhetdex`. Please use
[markdown](http://daringfireball.net/projects/markdown/syntax) syntax so it can
be easily converted to html or wiki format if needed **and** remains very
readable

## Installation
The repository can be obtained from the svn repository using the following
command

    svn checkout svn://luna.mpe.mpg.de/pyhetdex/trunk

To use the `pyhetdex` library it's possible to use one of the following options

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

4. It is also possible to install `pyhetdex` directly from the svn repository:

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


##Dependencies

    numpy
    scipy
    astropy

NOTE: as `pyfits` has been integrated into `astropy` and going out of support
and since the latter provides much more functionalities that the former, we do
not support pyfits.


# pyhetdex

`pyhetdex` is a python library designed to collect code can could be used by
different project like
[`VIRUS Data Analysis Tool`](https://luna.mpe.mpg.de/wikihetdex/index.php/VIRUS_Data_Analysis_Tool),
[`VIRUS Health Check`](https://luna.mpe.mpg.de/wikihetdex/index.php/VIRUS_Health_Check),
[`simhetdex`](https://luna.mpe.mpg.de/wikihetdex/index.php/VIRUS_Data_Simulation_Framework)
or
[`Cure-WISE`](https://luna.mpe.mpg.de/wikihetdex/index.php/Overview_of_Cure-WISE).

## Official documentation

The official documentation can be found
[online](http://www.mpe.mpg.de/~montefra/documentation/pyhetdex).

We use the [Redmine issue
tracker](https://luna.mpe.mpg.de/redmine/projects/pyhetdex) to register bugs,
feature requests and other issues.

## Installation

The recommended way to install pyhetdex is using
[pip](https://pip.pypa.io/en/latest/):

    pip install --extra-index-url https://gate.mpe.mpg.de/pypi/simple/ pyhetdex

It's possible to set the extra index URL permanently by adding the following
lines to the ``$HOME/.pip/pip.conf`` file:

    [global]
    extra-index-url = https://gate.mpe.mpg.de/pypi/simple

or exporting the environment variable:

    export PIP_EXTRA_INDEX_URL=https://gate.mpe.mpg.de/pypi/simple

The list of released versions can be seen [on the MPE pypi
server](https://gate.mpe.mpg.de/pypi/simple/pyhetdex/). A specific version can
be installed using
[specifiers](https://pip.pypa.io/en/stable/reference/pip_install/#requirement-specifiers>),
e.g. issuing ``pip install pyhetdex==0.5``.

``pip`` will take care of installing all the pyhetdex dependences

We suggest you install pyhetdex into a
[virtualenv](https://virtualenv.pypa.io/en/stable/), in an
[anaconda](https://www.continuum.io/downloads)/[conda](http://conda.pydata.org/docs/index.html)
or in similar environments.

Of course it is also possible to install pyhetdex without any of the above with::

    pip install --user --extra-index-url https://gate.mpe.mpg.de/pypi/simple/ pyhetdex

This way the pyhetdex executables are installed in ``$HOME/.local/bin``, so make
sure to add this to the environment variable ``PATH`` to be able to easily use
them on the command line. The use of ``sudo`` when installing with pip is
[discouraged](http://stackoverflow.com/questions/21055859/what-are-the-risks-of-running-sudo-pip)
and potentially harmful.

## Dependencies

Mandatory

    six
    numpy
    matplotlib
    scipy
    astropy>=1
    Pillow

Optional:

    test: pytest-cov
          pytest-xdist
          pytest-catchlog
          pytest
          tox
    documentation: sphinx
                   numpydoc
                   alabaster

## Development

If you want to help developing pyhetdex, please follow the information about
[installation](http://www.mpe.mpg.de/~montefra/documentation/pyhetdex/latest/install.html#development)
and
[contribution](http://www.mpe.mpg.de/~montefra/documentation/pyhetdex/latest/contributions.html)
and get in touch with the other developers.

## Notes

Please use [markdown](http://daringfireball.net/projects/markdown/syntax) syntax
so it can be easily converted to html or wiki format if needed **and** remains
very readable


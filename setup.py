try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup
import os


# retrieve version number from `Version` file
versionf = os.path.join(os.path.split(__file__)[0], 'VERSION')

def extract_versions():
    """
    Extracts version values from the main pyhetdex __init__.py and
    returns them as a dictionary.
    Taken from matplotlib/setupext.py
    """
    with open('pyhetdex/__init__.py') as fd:
        for line in fd:
            if (line.startswith('__version__')):
                version = line.split('=')[1].strip().strip('"')
                break
    return version

setup(
    # package description and version
    name="pyhetdex",
    version=extract_versions(),
    author="Francesco Montesano",
    author_email="montefra@mpe.mpg.de",
    description="Heterogeneous collection of HETDEX-related functionalities",
    # long_description="",

    # list of packages and data
    packages=[ 'pyhetdex'
             , 'pyhetdex.astrometry'
             , 'pyhetdex.common'
             , 'pyhetdex.cure'
             , 'pyhetdex.het'
             , 'pyhetdex.ltl'
             , 'pyhetdex.tools'
             , 'pyhetdex.tools.analysis'
             ],
    # don't zip when installing
    zip_safe=False,

    # dependences
    install_requires=['numpy'
                     , 'scipy'
                     , 'astropy'
                     ],

    # tests
    # test_suite=?,
)

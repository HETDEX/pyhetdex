import sys

from setuptools import setup, find_packages
from setuptools.command.test import test


def extract_version():
    """
    Extracts version values from the main pyhetdex __init__.py and
    returns it.
    Taken from matplotlib/setupext.py
    """
    with open('pyhetdex/__init__.py') as fd:
        for line in fd:
            if (line.startswith('__version__')):
                version = line.split('=')[1].strip().strip('"')
                break
    return version


# custom test command using py.test

class PyTest(test):
    user_options = [('pytest-args=', 'a', "Arguments to pass to py.test")]

    def initialize_options(self):
        test.initialize_options(self)
        self.pytest_args = []

    def finalize_options(self):
        test.finalize_options(self)
        self.test_args = []
        self.test_suite = True

    def run_tests(self):
        # import here, cause outside the eggs aren't loaded
        import pytest
        errno = pytest.main(self.pytest_args)
        sys.exit(errno)


class Tox(test):
    description = "run unit tests in virtual environments using tox"
    user_options = [('tox-args=', 'a', "Arguments to pass to tox")]

    def initialize_options(self):
        test.initialize_options(self)
        self.tox_args = None

    def finalize_options(self):
        test.finalize_options(self)
        self.test_args = []
        self.test_suite = True

    def run_tests(self):
        if self.distribution.install_requires:
            self.distribution.fetch_build_eggs(
                self.distribution.install_requires)
        if self.distribution.tox_requires:
            self.distribution.fetch_build_eggs(self.distribution.tox_requires)
        # import here, cause outside the eggs aren't loaded
        import tox
        import shlex
        args = self.tox_args
        if args:
            args = shlex.split(self.tox_args)
        else:
            args = ""
        errno = tox.cmdline(args=args)
        sys.exit(errno)


def extras_require(key=None):
    """Deal with extra requirements

    Parameters
    ----------
    key : string, optional
        if not none, returns the requirements only for the given option

    Returns
    -------
    dictionary of requirements
    if key is not None: list of requirements
    """
    req_dic = {'doc': ['sphinx', 'numpydoc', 'alabaster'],
               }

    req_dic['livedoc'] = req_dic['doc'] + ['sphinx-autobuild>=0.5.2', ]

    req_dic['test'] = ['pytest-cov', 'pytest']
    req_dic['tox'] = ['tox', ]

    req_dic['all'] = set(sum((v for v in req_dic.values()), []))

    if key:
        return req_dic[key]
    else:
        return req_dic


entry_points = {'console_scripts':
                ['dither_file = pyhetdex.het.dither:create_dither_file',
                 'reconstructIFU = pyhetdex.het.reconstruct_ifu:create_quick_reconstruction',
                 'datacube2rgb = pyhetdex.tools.datacube2rgb:main']}

# setuptools customisation
distutils_ext = {'distutils.setup_keywords': [
                    "tox_requires = setuptools.dist:check_requirements", ]
                 }
entry_points.update(distutils_ext)

setup(
    # package description and version
    name="pyhetdex",
    version="0.2.1",
    author="HETDEX collaboration",
    author_email="montefra@mpe.mpg.de",
    description="Heterogeneous collection of HETDEX-related functionalities",
    long_description=open("README.md").read(),

    # custom test class
    cmdclass={
        'test': PyTest,
        'tox': Tox,
    },

    # list of packages and data
    packages=find_packages(),
    # don't zip when installing
    zip_safe=False,

    entry_points=entry_points,

    # dependences
    install_requires=['numpy', 'scipy', 'astropy>=1', 'Pillow', 'matplotlib',
                      'six'],
    extras_require=extras_require(),

    # tests
    tests_require=extras_require('test'),
    tox_requires=extras_require('tox'),

    classifiers=["Development Status :: 3 - Alpha",
                 "Environment :: Console",
                 "Intended Audience :: Developers",
                 "Intended Audience :: Science/Research",
                 "License :: OSI Approved :: GNU General Public License (GPL)",
                 "Operating System :: Unix",
                 "Programming Language :: Python :: 2.7",
                 "Programming Language :: Python :: 3.4",
                 "Programming Language :: Python :: 3.5",
                 "Topic :: Scientific/Engineering :: Astronomy",
                 "Topic :: Utilities",
                 ]
)

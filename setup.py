from setuptools import setup, find_packages
import os


def extract_version():
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
    version=extract_version(),
    author="Francesco Montesano",
    author_email="montefra@mpe.mpg.de",
    description="Heterogeneous collection of HETDEX-related functionalities",
    long_description=open("README.md").read(),

    # list of packages and data
    packages=find_packages(),
    # don't zip when installing
    zip_safe=False,

    # dependences
    install_requires=['numpy', 'scipy', 'astropy==1', 'Pillow', 'matplotlib'],

    extras_require={'nosetests': ['nose>=1', 'coverage'],
                    'doc': ['sphinx', 'numpydoc']},

    # tests
    test_suite='nose.collector',
)

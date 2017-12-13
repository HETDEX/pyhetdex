import sys
try:
    import setuptools
except ImportError:
    from ez_setup import use_setuptools
    use_setuptools()

from setuptools import setup, find_packages


install_requires = ['six', 'numpy', 'matplotlib', 'scipy',
                    'astropy>=1.2, !=1.3.3', 'Pillow', ]
if sys.version_info < (3, 2):  # add backported configparser module if py < 3.2
    install_requires.append('configparser')


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
    req_dic = {'doc': ['sphinx>=1.4', 'numpydoc', 'alabaster'],
               }

    req_dic['livedoc'] = req_dic['doc'] + ['sphinx-autobuild>=0.5.2', ]

    req_dic['test'] = ['pytest-cov', 'pytest-xdist', 'pytest>=3.3.0', 'peewee']
    req_dic['tox'] = ['tox', ]

    req_dic['all'] = set(sum((v for v in req_dic.values()), []))

    if key:
        return req_dic[key]
    else:
        return req_dic


entry_points = {'console_scripts':
                ['dither_file = pyhetdex.het.dither:create_dither_file',
                 'reconstructIFU ='
                 ' pyhetdex.het.reconstruct_ifu:create_quick_reconstruction',
                 'datacube2rgb = pyhetdex.tools.datacube2rgb:main',
                 'add_fluxes_to_randoms ='
                 'pyhetdex.randoms.generate_randoms:add_fluxes_and_snr_to_randoms_cmd',
                 'generate_randoms ='
                 'pyhetdex.randoms.generate_randoms:generate_randoms_cmd',
                 'add_ifu_xy ='
                 'pyhetdex.coordinates.astrometry:add_ifu_xy',
                 'add_ra_dec ='
                 'pyhetdex.coordinates.astrometry:add_ra_dec',
                 'add_wcs ='
                 'pyhetdex.coordinates.astrometry:add_wcs',
                 'xy_to_ra_dec ='
                 'pyhetdex.coordinates.astrometry:xy_to_ra_dec',
                 'generate_hetdex_mask='
                 'pyhetdex.tools.create_mask:generate_mangle_polyfile'
                 ]}

setup(
    # package description and version
    name="pyhetdex",
    version="0.12.0-post",
    author="HETDEX collaboration",
    author_email="montefra@mpe.mpg.de",
    description="Heterogeneous collection of HETDEX-related functionalities",
    long_description=open("README.md").read(),

    # list of packages and data
    packages=find_packages(),
    include_package_data=True,
    # don't zip when installing
    zip_safe=False,

    entry_points=entry_points,

    # dependences
    setup_requires=['pytest-runner', ],
    install_requires=install_requires,
    extras_require=extras_require(),
    # tests
    tests_require=extras_require('test'),

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

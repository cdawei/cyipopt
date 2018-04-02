# -*- coding: utf-8 -*-
"""
cyipot: Python wrapper for the Ipopt optimization package, written in Cython.

Copyright (C) 2012 Amit Aides, 2015 Matthias Kümmerer
Author: Matthias Kümmerer <matthias.kuemmerer@bethgelab.org>
(originally Author: Amit Aides <amitibo@tx.technion.ac.il>)
URL: <https://bitbucket.org/amitibo/cyipopt>
License: EPL 1.0
"""

import sys
import os.path
from distutils.sysconfig import get_python_lib
from distutils import sysconfig
import subprocess as sp

from setuptools import setup
from setuptools.extension import Extension
from Cython.Distutils import build_ext
import Cython.Distutils
import Cython.Compiler.Options
from Cython.Build import cythonize
import numpy as np
import six

exec(open('ipopt/version.py').read())

PACKAGE_NAME = 'ipopt'
VERSION = __version__
DESCRIPTION = 'A Cython wrapper to the IPOPT optimization package'
AUTHOR = 'Matthias Kümmerer'
EMAIL = 'matthias.kuemmerer@bethgelab.org'
URL = "https://github.com/matthias-k/cyipopt"
DEPENDENCIES = ['numpy', 'scipy', 'cython', 'six', 'future', 'setuptools']


def main_win32():
    IPOPT_INCLUDE_DIRS = ['include_mt/coin', np.get_include()]
    IPOPT_LIBS = ['Ipopt39', 'IpoptFSS']
    IPOPT_LIB_DIRS = ['lib_mt/x64/release']
    IPOPT_DLL = ['Ipopt39.dll', 'IpoptFSS39.dll']

    setup(
        name=PACKAGE_NAME,
        version=VERSION,
        description=DESCRIPTION,
        author=AUTHOR,
        author_email=EMAIL,
        url=URL,
        packages=[PACKAGE_NAME],
        install_requires=DEPENDENCIES,
        cmdclass={'build_ext': build_ext},
        ext_modules=[
            Extension(
                PACKAGE_NAME + '.' + 'cyipopt',
                ['src/cyipopt.pyx'],
                include_dirs=IPOPT_INCLUDE_DIRS,
                libraries=IPOPT_LIBS,
                library_dirs=IPOPT_LIB_DIRS
            )
        ],
        data_files=[(os.path.join(get_python_lib(), PACKAGE_NAME),
                     [os.path.join(IPOPT_LIB_DIRS[0], dll)
                      for dll in IPOPT_DLL])] if IPOPT_DLL else None
    )


def pkgconfig(*packages, **kw):
    """Based on http://code.activestate.com/recipes/502261-python-distutils-pkg-config/#c2"""

    flag_map = {'-I': 'include_dirs', '-L': 'library_dirs', '-l': 'libraries'}
    output = sp.Popen(["pkg-config", "--libs", "--cflags"] + list(packages),
                      stdout=sp.PIPE).communicate()[0]
    if six.PY3:
        output = output.decode('utf8')
    for token in output.split():
        if token[:2] in flag_map:
            kw.setdefault(flag_map.get(token[:2]), []).append(token[2:])
        else:
            kw.setdefault('extra_compile_args', []).append(token)

    kw['include_dirs'] += [np.get_include()]

    return kw


def main_unix():
    IPOPT_INCLUDE_DIRS = os.path.expanduser('~/apps/miniconda3/include/coin')
    IPOPT_LIB_DIRS = os.path.expanduser('~/apps/miniconda3/lib')
    IPOPT_LIBS = 'ipopt'
    CFLAGS = sysconfig._config_vars['CFLAGS']
    sysconfig._config_vars['CFLAGS'] = CFLAGS.replace(' -g ', ' ').replace(' -DNDEBUG ', ' ')
    extra_flags = ['-march=haswell', '-v']
    setup(name=PACKAGE_NAME,
          version=VERSION,
          packages=[PACKAGE_NAME],
          #install_requires=DEPENDENCIES,
          #cmdclass={'build_ext': Cython.Distutils.build_ext},
          include_package_data=True,
          ext_modules=cythonize([Extension(name='cyipopt', 
                                 sources=['src/cyipopt.pyx'],
                                 include_dirs=[IPOPT_INCLUDE_DIRS],
                                 library_dirs=[IPOPT_LIB_DIRS],
                                 libraries=[IPOPT_LIBS],
                                 extra_compile_args=extra_flags,
                                 language='c')]))
#                                 **pkgconfig('ipopt'))])

if __name__ == '__main__':
    if sys.platform == 'win32':
        main_win32()
    else:
        main_unix()

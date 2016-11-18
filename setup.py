import sys

from setuptools import setup, Extension


def has_option(name):
    try:
        sys.argv.remove('--%s' % name)
        return True
    except ValueError:
        return False

USE_CYTHON = has_option('cython')

ext = '.pyx' if USE_CYTHON else '.c'

extensions = [
    Extension('contracts.contract', ['contracts/contract'+ext]),
    Extension('contracts.exceptions', ['contracts/exceptions'+ext]),
    Extension('contracts.fields', ['contracts/fields'+ext]),
    Extension('contracts.validators', ['contracts/validators'+ext]),
    Extension('contracts.utils', ['contracts/utils'+ext]),
]

if USE_CYTHON:
    from Cython.Build import cythonize
    extensions = cythonize(extensions)

setup(
    name='contracts',
    version='0.1',
    packages=['contracts'],
    install_requires=['ciso8601'],
    ext_modules=extensions
)

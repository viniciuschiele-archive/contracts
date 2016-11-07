from distutils.core import setup
from Cython.Build import cythonize

setup(
    ext_modules=cythonize(('contracts/__init__.pyx',
                           'contracts/exceptions.pyx',
                           'contracts/fields.pyx',
                           'contracts/validators.pyx',
                           'contracts/utils/__init__.pyx',
                           'contracts/utils/formatting.pyx'))
)


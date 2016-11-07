from distutils.core import setup
from Cython.Build import cythonize

setup(
    ext_modules=cythonize(('contracts/exceptions.py',
                           'contracts/fields.py',
                           'contracts/validators.py',
                           'contracts/utils/__init__.py',
                           'contracts/utils/formatting.py'))
)


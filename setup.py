from distutils.core import setup
from Cython.Build import cythonize

setup(
    name='Contracts',
    version='0.1',
    packages=['contracts'],
    install_requires=['cython', 'ciso8601'],
    ext_modules=cythonize(('contracts/__init__.py',
                           'contracts/contract.pyx',
                           'contracts/exceptions.pyx',
                           'contracts/fields.pyx',
                           'contracts/validators.pyx',
                           'contracts/utils/__init__.pyx'))
)

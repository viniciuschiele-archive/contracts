#!/usr/bin/env bash
find ./contracts -type f -name '*.so' -delete
find ./contracts -type f -name '*.c' -delete
find ./contracts -type f -name '*.h' -delete

python setup.py build_ext --inplace --cython

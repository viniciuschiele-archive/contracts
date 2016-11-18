"""
Handles exceptions raised by Contracts.
"""


cdef class ValidationError(Exception):
    cdef public object messages
    cdef public str field_name

"""
Handles exceptions raised by Contracts.
"""


cdef class ValidationError(Exception):
    cdef public object message
    cdef public dict extra

    cpdef dict as_dict(self, str default_field_name)

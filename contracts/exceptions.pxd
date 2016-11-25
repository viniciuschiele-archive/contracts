"""
Handles exceptions raised by Contracts.
"""


cdef class ValidationError(Exception):
    cdef public object messages
    cdef public list field_names


cdef class ContractError(ValidationError):
    cpdef add_error(self, ValidationError error)

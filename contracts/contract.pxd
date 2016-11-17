from .fields cimport Field


cdef class BaseContract(Field):
    cdef public object many
    cdef public object only
    cdef public object exclude
    cdef list _load_fields
    cdef list _dump_fields

    cpdef pre_dump(self, data)
    cpdef post_dump(self, data, original_data)
    cpdef pre_dump_many(self, data)
    cpdef post_dump_many(self, data, original_data)

    cpdef pre_load(self, data)
    cpdef post_load(self, data, original_data)
    cpdef pre_load_many(self, data)
    cpdef post_load_many(self, data, original_data)

    cpdef _dump(self, data)
    cpdef _load(self, data)

    cdef inline _get_value(self, data, field_name)
    cdef inline _dump_many(self, data)
    cdef inline _dump_single(self, data)
    cdef inline _load_many(self, data)
    cdef inline _load_single(self, data)
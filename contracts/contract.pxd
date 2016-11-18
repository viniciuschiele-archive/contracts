from . cimport abc


cdef class BaseContract(abc.Contract):
    cdef public bint many
    cdef public set only
    cdef public set exclude
    cdef list _load_fields
    cdef list _dump_fields

    cpdef object pre_dump(self, object data)
    cpdef object post_dump(self, object data, object original_data)
    cpdef object pre_dump_many(self, object data)
    cpdef object post_dump_many(self, object data, object original_data)

    cpdef object pre_load(self, object data)
    cpdef object post_load(self, object data, object original_data)
    cpdef object pre_load_many(self, object data)
    cpdef object post_load_many(self, object data, object original_data)

    cpdef _prepare_fields(self)
    cpdef _prepare_nested_fields(self, str option_name, set field_names)

    cdef inline object _get_value(self, object data, str field_name)
    cdef inline object _dump_many(self, object data)
    cdef inline object _dump_single(self, object data)
    cdef inline object _load_many(self, object data)
    cdef inline object _load_single(self, object data)
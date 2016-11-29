cdef class Context(object):
    cdef public BaseContract contract
    cdef public object contract_data
    cdef public dict _data


cdef class BaseContract(object):
    cdef public bint many
    cdef public set only
    cdef public set exclude
    cdef public bint partial
    cdef public dict fields

    cdef list _load_fields
    cdef list _dump_fields
    cdef int[:] _hooks

    cpdef object dump(self, object value, Context context=*)
    cpdef object load(self, object value, Context context=*)

    cpdef _prepare_fields(self)
    cpdef _prepare_nested_fields(self, str option_name, set field_names)

    cpdef object _pre_dump(self, object data, Context context)
    cpdef object _pre_dump_many(self, object data, Context context)
    cpdef object _pre_load(self, object data, Context context)
    cpdef object _pre_load_many(self, object data, Context context)

    cpdef object _post_dump(self, object data, Context context)
    cpdef object _post_dump_many(self, object data, Context context)
    cpdef object _post_load(self, object data, Context context)
    cpdef object _post_load_many(self, object data, Context context)

    cdef inline object _get_value(self, object data, str field_name)
    cdef inline object _dump_many(self, object data, Context context)
    cdef inline object _dump_single(self, object data, Context context)
    cdef inline object _load_many(self, object data, Context context)
    cdef inline object _load_single(self, object data, Context context)
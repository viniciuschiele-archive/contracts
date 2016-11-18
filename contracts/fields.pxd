from . cimport abc


cdef class Field(abc.Field):
    cdef public str name
    cdef public abc.Contract parent
    cdef public bint dump_only
    cdef public bint load_only
    cdef public object default_
    cdef public bint allow_none
    cdef public str dump_to
    cdef public str load_from
    cdef public bint required
    cdef public list validators
    cdef public dict error_messages

    cpdef object _get_default(self)
    cpdef object _dump(self, object value)
    cpdef object _load(self, object value)
    cpdef _validate(self, object value)


cdef class Boolean(Field):
    pass


cdef class Date(Field):
    pass


cdef class DateTime(Field):
    pass


cdef class Float(Field):
    cdef public object min_value
    cdef public object max_value


cdef class Integer(Field):
    cdef public object min_value
    cdef public object max_value


cdef class List(Field):
    cdef public abc.Field child
    cdef public bint allow_empty


cdef class Method(Field):
    cdef public str dump_method_name
    cdef public str load_method_name


cdef class Nested(Field):
    cdef public object nested
    cdef public bint many
    cdef public set only
    cdef public set exclude
    cdef public abc.Contract _instance


cdef class String(Field):
    cdef public bint allow_blank
    cdef public bint trim_whitespace
    cdef public object min_length
    cdef public object max_length


cdef class UUID(Field):
    pass

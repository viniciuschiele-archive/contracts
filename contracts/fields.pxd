cdef class Field(object):
    cdef public object dump_only
    cdef public object load_only
    cdef public object default_
    cdef public object allow_none
    cdef public str dump_to
    cdef public str load_from
    cdef public object required
    cdef public str name
    cdef public object parent
    cdef public list validators
    cdef public dict error_messages

    cpdef bind(self, name, parent)
    cpdef dump(self, value)
    cpdef load(self, value)

    cpdef _get_default(self)
    cpdef _dump(self, value)
    cpdef _load(self, value)
    cpdef _validate(self, value)


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
    cdef public object child
    cdef public object allow_empty


cdef class Method(Field):
    cdef public object dump_method_name
    cdef public object load_method_name


cdef class Nested(Field):
    cdef public object nested
    cdef public object many
    cdef public object only
    cdef public object exclude
    cdef public object _instance


cdef class String(Field):
    cdef public object allow_blank
    cdef public object trim_whitespace
    cdef public object min_length
    cdef public object max_length


cdef class UUID(Field):
    pass

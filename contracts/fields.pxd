from cpython.datetime cimport datetime

from .contract cimport Context, BaseContract


cdef class Field(object):
    cdef public str name
    cdef public object parent
    cdef public bint dump_only
    cdef public bint load_only
    cdef public object default_value
    cdef public bint allow_none
    cdef public str dump_to
    cdef public str load_from
    cdef public bint required
    cdef public list validators
    cdef public dict error_messages

    cpdef bind(self, str name, object parent)
    cpdef object dump(self, object value, Context context)
    cpdef object load(self, object value, Context context)

    cdef _prepare_error_messages(self, dict error_messages)
    cpdef object _get_default(self)
    cpdef object _dump(self, object value, Context context)
    cpdef object _load(self, object value, Context context)
    cpdef _validate(self, object value)


cdef class Boolean(Field):
    cdef public set _true_values
    cdef public set _false_values


cdef class Date(Field):
    pass


cdef class DateTime(Field):
    cdef public object default_timezone

    cpdef _enforce_timezone(self, datetime value)


cdef class Float(Field):
    cdef public object min_value
    cdef public object max_value


cdef class Function(Field):
    cdef public object dump_func
    cdef public object load_func


cdef class Integer(Field):
    cdef public object min_value
    cdef public object max_value


cdef class List(Field):
    cdef public Field child
    cdef public bint allow_empty


cdef class Method(Field):
    cdef public str dump_method_name
    cdef public str load_method_name
    cdef public object _dump_method
    cdef public object _load_method

    cpdef object _get_method(self, str method_name)


cdef class Nested(Field):
    cdef public object nested
    cdef public bint many
    cdef public set only
    cdef public set exclude
    cdef public BaseContract _instance

    cdef inline BaseContract _get_instance(self)


cdef class String(Field):
    cdef public bint allow_blank
    cdef public bint trim_whitespace
    cdef public object min_length
    cdef public object max_length


cdef class UUID(Field):
    cdef public str dump_format

cdef class Contract(object):
    cpdef object dump(self, object value)
    cpdef object load(self, object value)


cdef class Field(object):
    cpdef bind(self, str name, Contract parent)
    cpdef object dump(self, object value)
    cpdef object load(self, object value)

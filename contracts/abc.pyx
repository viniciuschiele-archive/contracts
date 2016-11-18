cdef class Contract(object):
    cpdef object dump(self, object value):
        raise NotImplemented()

    cpdef object load(self, object value):
        raise NotImplemented()


cdef class Field(object):
    cpdef bind(self, str name, Contract parent):
        raise NotImplemented()

    cpdef object dump(self, object value):
        raise NotImplemented()

    cpdef object load(self, object value):
        raise NotImplemented()

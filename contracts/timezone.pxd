from cpython.datetime cimport datetime, tzinfo


cdef class UTC(tzinfo):
    pass


cpdef is_aware(datetime value)
cpdef make_aware(datetime value, tzinfo timezone)
cpdef make_naive(datetime value, tzinfo timezone)

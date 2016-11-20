"""
Provides various validators.
"""

cdef class Validator:
    """
    A base class from which all validator classes should inherit.
    :param dict error_messages: The error messages for various kinds of errors.
    """
    cdef public dict error_messages


cdef class Choice(Validator):
    """
    Validator which succeeds if the `value` is a member of the `choices`.
    :param iterable choices: An array of valid values.
    :param dict error_messages: The error messages for various kinds of errors.
    """
    cdef public tuple choices


cdef class Length(Validator):
    """
    Validator which succeeds if the value passed to it has a length between a minimum and maximum.
    :param int min_length: The minimum length. If not provided, minimum length will not be checked.
    :param int max_length: The maximum length. If not provided, maximum length will not be checked.
    :param int equal_length: The exact length. If provided, maximum and minimum length will not be checked.
    :param dict error_messages: The error messages for various kinds of errors.
    """
    cdef public object min_length
    cdef public object max_length
    cdef public object equal_length


cdef class Range(Validator):
    """
    Validator which succeeds if the value it is passed is greater
    or equal to `min_value` and less than or equal to `max_value`.
    :param min_value: The minimum value (lower bound). If not provided, minimum value will not be checked.
    :param max_value: The maximum value (upper bound). If not provided, maximum value will not be checked.
    :param dict error_messages: The error messages for various kinds of errors.
    """
    cdef public object min_value
    cdef public object max_value



cdef class Regex(Validator):
    """
    Validator which succeeds if the `value` matches with the regex.
    :param regex: The regular expression string to use. Can also be a compiled regular expression pattern.
    :param dict error_messages: The error messages for various kinds of errors.
    """
    cdef public object regex


cdef class UUID(Validator):
    """
    Validator which succeeds if the value is an UUID.
    :param dict error_messages: The error messages for various kinds of errors.
    """
    pass

"""
Handles exceptions raised by Contracts.
"""


cdef class ValidationError(Exception):
    def __init__(self, message, field_name=None):
        if not isinstance(message, dict) and not isinstance(message, list):
            self.messages = [message]
        else:
            self.messages = message

        self.field_name = field_name

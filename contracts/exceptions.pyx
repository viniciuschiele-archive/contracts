"""
Handles exceptions raised by Contracts.
"""


cdef class ValidationError(Exception):
    def __init__(self, object message, list field_names=None):
        if not isinstance(message, list):
            message = [message]

        self.messages = message
        self.field_names = field_names


cdef class ContractError(ValidationError):
    def __init__(self, list errors=None):
        self.messages = {}

        if errors:
            for error in errors:
                self.add_error(error)

    cpdef add_error(self, ValidationError error):
        cdef object field_messages
        cdef list field_names = error.field_names or ['_contract']

        for field_name in field_names:
            field_messages = self.messages.get(field_name, None)

            if field_messages is None:
                self.messages[field_name] = error.messages

            elif isinstance(error.messages, list):
                field_messages.extend(error.messages)

            elif isinstance(error.messages, dict):
                field_messages.update(error.messages)

            else:
                raise ValueError('Expected list or dict, got ' + str(type(error.messages)))

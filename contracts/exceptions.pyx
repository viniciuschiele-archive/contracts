"""
Handles exceptions raised by Contracts.
"""


cdef class ValidationError(Exception):
    def __init__(self, message, **kwargs):
        if isinstance(message, ValidationError):
            self.message = message.message
            self.extra = message.extra

        elif isinstance(message, dict):
            messages = {}

            for field, message in message.items():
                if isinstance(message, ValidationError):
                    messages[field] = message
                else:
                    messages[field] = ValidationError(message)

            self.message = messages

        elif isinstance(message, list):
            messages = []

            for message in message:
                if isinstance(message, str):
                    messages.append(ValidationError(message, **kwargs))
                elif isinstance(message, ValidationError):
                    messages.append(message)
                else:
                    raise Exception('Expected str or ValidationError')

            self.message = messages

        elif isinstance(message, str):
            self.message = message
            self.extra = kwargs

        else:
            raise Exception('Expected str, list, dict or ValidationError')

    cpdef dict as_dict(self, str default_field_name):
        if isinstance(self.message, dict):
            return self.message

        if isinstance(self.message, list):
            return {default_field_name: self.message}

        d = {default_field_name: self.message}
        d.update(self.extra)

        return d

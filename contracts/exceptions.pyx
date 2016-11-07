"""
Handles exceptions raised by Flask WebAPI.
"""


class ValidationError(Exception):
    def __init__(self, message, **kwargs):
        # if `message` is a dict the key is
        # the name of the field and the value is
        # actual message.
        if isinstance(message, dict):
            result = {}

            for field, messages in message.items():
                if not isinstance(messages, ValidationError):
                    messages = ValidationError(messages)

                if isinstance(messages.message, str):
                    result[field] = [messages]
                else:
                    result[field] = messages.message

            self.message = result
            self.kwargs = {}

        elif isinstance(message, list):
            result = []
            for msg in message:
                if not isinstance(msg, ValidationError):
                    if isinstance(msg, dict):
                        msg = ValidationError(**msg)
                    else:
                        msg = ValidationError(msg)

                result.append(msg)

            if len(result) == 1:
                self.message = result[0].message
                self.kwargs = result[0].kwargs
            else:
                self.message = result
                self.kwargs = {}

        else:
            self.message = str(message)
            self.kwargs = kwargs

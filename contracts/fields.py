"""
fields ...
"""

from . import abc
from .io import missing


class Field(abc.Field):
    """
    Field ...
    """
    def __init__(self, required=None, default=missing):
        self.default = default

        # If `required` is unset, then use `True` unless a default is provided.
        if required is None:
            self.required = default is missing
        else:
            self.required = required

    def read_naive(self, reader):
        """
        read_naive ...
        """
        return reader.read(self.name)

    def write_naive(self, value, writer):
        """
        write_naive ...
        """
        return writer.write(self.name, value)

    def _fail(self, code):
        """
        _fail ...
        """
        pass


class String(Field):
    """
    String ...
    """

    def read(self, reader):
        """
        read ...
        """
        value = reader.read(self.name)

        if value is None:
            # if self.allow_none:
                # return None
            self._fail('null')

        if value is missing:
            if self.required:
                self._fail('required')

            return self.default

        return str(value)

    def write(self, value, writer):
        """
        write ...
        """
        # if value is missing:
        #     return

        writer.write(self.name, str(value))

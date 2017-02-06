"""
contracts ...
"""

from .io import create_reader, create_writer, missing


class Contract(object):
    """
    Contract ...
    """
    read_type = dict

    def __init__(self):
        super(Contract, self).__init__()
        self.fields = {}

    def read(self, reader):
        """
        read ...
        """
        writer = create_writer(self.read_type)

        for field in self.fields.values():
            value = field.read(reader)

            if value is not missing:
                field.write_naive(value, writer)

        return writer.data

    def write(self, value, writer):
        """
        write ...
        """
        reader = create_reader(value)

        for field in self.fields.values():
            value = field.read_naive(reader)

            if value is not missing:
                field.write_naive(value, writer)

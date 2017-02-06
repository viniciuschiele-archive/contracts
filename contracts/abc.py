"""
abc ...
"""

class Field(object):
    """
    Field ...
    """
    name = None

    def bind(self, name):
        """
        bind ...
        """
        self.name = name

    def read(self, reader):
        """
        read ...
        """
        pass

    def read_naive(self, reader):
        """
        read_naive ...
        """
        pass

    def write(self, value, writer):
        """
        write ...
        """
        pass
    def write_naive(self, value, writer):
        """
        write ...
        """
        pass

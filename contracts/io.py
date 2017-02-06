"""
readers ...
"""

class missing(object):
    """
    missing ...
    """
    pass


class Reader(object):
    """
    Reader ...
    """
    def read(self, key):
        """
        read ...
        """
        pass


class DictReader(Reader):
    """
    DictReader ...
    """
    def __init__(self, data):
        self._data = data

    def read(self, key):
        """
        read ...
        """
        return self._data.get(key, missing)


class Writer(object):
    """
    Reader ...
    """
    @property
    def data(self):
        """
        data ...
        """
        pass

    def write(self, key, value):
        """
        write ...
        """
        pass


class DictWriter(Writer):
    """
    DictWriter ...
    """
    def __init__(self):
        self._data = {}

    @property
    def data(self):
        """
        data ...
        """
        return self._data

    def write(self, key, value):
        """
        write ...
        """
        self._data[key] = value


def create_reader(value):
    """
    create_reader ...
    """
    return DictReader(value)


def create_writer(value_type):
    """
    create_write ...
    """
    if issubclass(value_type, dict):
        return DictWriter()

    return None

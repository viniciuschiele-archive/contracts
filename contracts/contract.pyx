cimport cython

from .exceptions cimport ValidationError
from .fields cimport Field
from .utils cimport missing


cdef class BaseContract(Field):
    default_error_messages = {
        'invalid': 'Invalid data. Expected a dictionary, but got {datatype}.'
    }

    _declared_fields = {}

    def __init__(self, many=False, only=None, exclude=None, **kwargs):
        super().__init__(**kwargs)

        self.many = many
        self.only = only
        self.exclude = exclude

        if self.only:
            field_names = set(self.only)
        else:
            field_names = set(self._declared_fields)

        if self.exclude:
            field_names = field_names - set(self.exclude)

        self._load_fields = []
        self._dump_fields = []

        for field_name, field in self._declared_fields.items():
            field.bind(field_name, self)

            if field.name in field_names:
                if field.load_only:
                    self._load_fields.append(field)
                elif field.dump_only:
                    self._dump_fields.append(field)
                else:
                    self._dump_fields.append(field)
                    self._load_fields.append(field)

    cpdef pre_dump(self, data):
        return data

    cpdef pre_dump_many(self, data):
        return data

    cpdef pre_load(self, data):
        return data

    cpdef pre_load_many(self, data):
        return data

    cpdef post_dump(self, data, original_data):
        return data

    cpdef post_dump_many(self, data, original_data):
        return data

    cpdef post_load(self, data, original_data):
        return data

    cpdef post_load_many(self, data, original_data):
        return data

    cdef inline _get_value(self, data, field_name):
        if isinstance(data, dict):
            return data.get(field_name, missing)

        return getattr(data, field_name, missing)

    cpdef _dump(self, data):
        if self.many:
            return self._dump_many(data)
        else:
            return self._dump_single(data)

    cdef inline _dump_many(self, data):
        items = []

        for item in data:
            items.append(self._dump_single(item))

        return items

    @cython.boundscheck(False)
    cdef inline _dump_single(self, data):
        data = self.pre_dump(data)

        cdef dict result = dict()

        cdef list dump_fields = self._dump_fields
        cdef int count = len(dump_fields)

        for i in range(count):
            field = dump_fields[i]

            raw = self._get_value(data, field.name)

            value = field.dump(raw)

            if value is not missing:
                result[field.dump_to] = value

        return self.post_dump(result, data)

    cpdef _load(self, data):
        if self.many:
            return self._load_many(data)
        else:
            return self._load_single(data)

    cdef inline _load_many(self, data):
        data = self.pre_load_many(data)

        items = []

        for item in data:
            items.append(self._load_single(item))

        items = self.post_load_many(items, data)

        return items

    @cython.boundscheck(False)
    cdef inline _load_single(self, data):
        if not isinstance(data, dict):
            self._fail('invalid', datatype=type(data).__name__)

        data = self.pre_load(data)

        cdef dict result = dict()
        cdef dict errors = dict()

        cdef list load_fields = self._load_fields
        cdef int count = len(load_fields)

        for i in range(count):
            field = load_fields[i]

            try:
                raw = self._get_value(data, field.load_from)

                value = field.load(raw)

                if value is not missing:
                    result[field.name] = value
            except ValidationError as err:
                errors[field.name] = err.messages

        if errors:
            raise ValidationError(errors)

        return self.post_load(result, data)


class ContractMeta(type):
    def __new__(mcs, name, bases, attrs):
        attrs['_declared_fields'] = mcs.get_declared_fields(bases, attrs)
        return super(ContractMeta, mcs).__new__(mcs, name, bases, attrs)

    @classmethod
    def get_declared_fields(mcs, bases, attrs):
        fields = []

        for attr_name, attr_value in list(attrs.items()):
            if isinstance(attr_value, Field):
                fields.append((attr_name, attrs.pop(attr_name)))

        for base in reversed(bases):
            if hasattr(base, '_declared_fields'):
                fields = list(base._declared_fields.items()) + fields

        return dict(fields)


class Contract(BaseContract, metaclass=ContractMeta):
    pass

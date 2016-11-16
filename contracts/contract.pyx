cimport cython

from .exceptions import ValidationError
from .fields cimport Field
from .utils import missing


cdef class Contract(Field):
    default_error_messages = {
        'invalid': 'Invalid data. Expected a dictionary, but got {datatype}.'
    }

    def __init__(self, many=False, only=None, partial=False, **kwargs):
        super().__init__(**kwargs)

        only = only or ()
        if not isinstance(only, (list, tuple)):
            raise AssertionError('`only` has to be a list or tuple')

        self.many = many
        self.only = only or ()
        self.partial = partial
        self.fields = self._get_declared_fields()

        if self.only:
            field_names = set(self.only)
        else:
            field_names = set(self.fields)

        self._load_fields = []
        self._dump_fields = []

        for field_name, field in self.fields.items():
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

    cpdef _get_declared_fields(self):
        fields = []

        for attr_name in dir(self):
            attr_value = getattr(self, attr_name, None)
            if isinstance(attr_value, Field):
                fields.append((attr_name, attr_value))

        #for attr_name, attr_value in list(attrs.items()):
        #    if isinstance(attr_value, Field):
        #        fields.append((attr_name, attrs.pop(attr_name)))

        #for base in reversed(bases):
        #    if hasattr(base, '_declared_fields'):
        #        fields = list(base._declared_fields.items()) + fields

        return dict(fields)

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

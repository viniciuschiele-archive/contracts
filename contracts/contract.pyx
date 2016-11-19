cimport cython

from collections import defaultdict
from . cimport abc
from .exceptions cimport ValidationError
from .fields cimport Field
from .utils cimport missing


cdef class BaseContract(abc.Contract):
    default_error_messages = {
        'invalid': 'Invalid data. Expected a dictionary, but got {datatype}.'
    }

    _declared_fields = {}

    def __init__(self, bint many=False, set only=None, set exclude=None):
        self.many = many
        self.only = only
        self.exclude = exclude

        self._load_fields = []
        self._dump_fields = []

        self._prepare_fields()

    cpdef object dump(self, object data, dict context=None):
        if self.many:
            return self._dump_many(data, context)
        else:
            return self._dump_single(data, context)

    cpdef object load(self, object data, dict context=None):
        if self.many:
            return self._load_many(data, context)
        else:
            return self._load_single(data, context)

    cpdef _prepare_fields(self):
        if self.only:
            self._prepare_nested_fields('only', self.only)
            self.only = set([field_name.split('.', 1)[0] for field_name in self.only])
            field_names = self.only
        else:
            field_names = set(self._declared_fields)

        if self.exclude:
            self._prepare_nested_fields('exclude', self.exclude)
            self.exclude = set([field_name for field_name in self.exclude if '.' not in field_name])
            field_names = field_names - set(self.exclude)

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

    cpdef _prepare_nested_fields(self, str option_name, set field_names):
        nested_fields = [name.split('.', 1) for name in field_names if '.' in name]

        nested_options = defaultdict(list)
        for parent, nested_names in nested_fields:
            nested_options[parent].append(nested_names)

        for key, options in iter(nested_options.items()):
            setattr(self._declared_fields[key], option_name, set(options))

    cdef inline object _get_value(self, object data, str field_name):
        if isinstance(data, dict):
            return data.get(field_name, missing)

        return getattr(data, field_name, missing)

    cdef inline object _dump_many(self, object data, dict context):
        data = self.pre_dump_many(data, context)

        cdef list items = []

        for item in data:
            items.append(self._dump_single(item, context))

        return self.post_dump_many(items, data, context)

    @cython.boundscheck(False)
    cdef inline object _dump_single(self, object data, dict context):
        data = self.pre_dump(data, context)

        cdef dict result = dict()

        cdef list dump_fields = self._dump_fields
        cdef int count = len(dump_fields)

        cdef Field field
        cdef object raw
        cdef object value

        for i in range(count):
            field = dump_fields[i]

            raw = self._get_value(data, field.name)

            value = field.dump(raw)

            if value is not missing:
                result[field.dump_to] = value

        return self.post_dump(result, data, context)

    cdef inline object _load_many(self, object data, dict context):
        data = self.pre_load_many(data, context)

        cdef list items = []

        for item in data:
            items.append(self._load_single(item, context))

        return self.post_load_many(items, data, context)

    @cython.boundscheck(False)
    cdef inline object _load_single(self, object data, dict context):
        if not isinstance(data, dict):
            self._fail('invalid', datatype=type(data).__name__)

        data = self.pre_load(data, context)

        cdef dict result = dict()
        cdef dict errors = None

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
                if errors:
                    errors = dict()
                errors[field.name] = err.messages

        if errors:
            raise ValidationError(errors)

        return self.post_load(result, data, context)

    cpdef object pre_dump(self, object data, dict context):
        return data

    cpdef object pre_dump_many(self, list data, dict context):
        return data

    cpdef object pre_load(self, object data, dict context):
        return data

    cpdef object pre_load_many(self, list data, dict context):
        return data

    cpdef object post_dump(self, object data, object original_data, dict context):
        return data

    cpdef object post_dump_many(self, list data, object original_data, dict context):
        return data

    cpdef object post_load(self, object data, object original_data, dict context):
        return data

    cpdef object post_load_many(self, list data, object original_data, dict context):
        return data


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

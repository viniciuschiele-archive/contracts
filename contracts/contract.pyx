cimport cython

from cpython cimport array
from collections import defaultdict
from .exceptions cimport ContractError, ValidationError
from .fields cimport Field
from .utils cimport missing


cdef list HOOK_NAMES = ['_pre_dump', '_pre_dump_many', '_post_dump', '_post_dump_many',
                        '_pre_load', '_pre_load_many', '_post_load', '_post_load_many']

cdef int HOOK_ENABLED = 1
cdef int HOOK_DISABLED = 0
cdef int HOOKS_COUNT = len(HOOK_NAMES)

cdef int PRE_DUMP_INDEX = 0
cdef int PRE_DUMP_MANY_INDEX = 1
cdef int POST_DUMP_INDEX = 2
cdef int POST_DUMP_MANY_INDEX = 3
cdef int PRE_LOAD_INDEX = 4
cdef int PRE_LOAD_MANY_INDEX = 5
cdef int POST_LOAD_INDEX = 6
cdef int POST_LOAD_MANY_INDEX = 7


cdef class Context(object):
    cpdef object get_item(self, str key):
        if self._data is None:
            return None

        return self._data.get(key)

    cpdef set_item(self, str key, object value):
        if self._data is None:
            self._data = dict()

        self._data[key] = value


cdef class BaseContract(object):
    default_error_messages = {
        'invalid': 'Invalid data. Expected a dictionary, but got {datatype}.'
    }

    _declared_fields = {}
    _declared_hooks = [HOOK_ENABLED] * HOOKS_COUNT

    def __init__(self, bint many=False, set only=None, set exclude=None, bint partial=False):
        self.many = many
        self.only = only
        self.exclude = exclude
        self.partial = partial
        self.fields = dict(self._declared_fields)

        self._load_fields = []
        self._dump_fields = []

        self._hooks = array.array('i', self._declared_hooks)

        self._prepare_fields()

    cpdef object dump(self, object data, Context context=None):
        if context is None:
            context = Context()

        previous_contract = context.contract
        previous_contract_data = context.contract_data

        context.contract = self
        context.contract_data = data

        if self.many:
            data = self._dump_many(data, context)
        else:
            data = self._dump_single(data, context)

        context.contract = previous_contract
        context.contract_data = previous_contract_data

        return data

    cpdef object load(self, object data, Context context=None):
        if context is None:
            context = Context()

        previous_contract = context.contract
        previous_contract_data = context.contract_data

        context.contract = self
        context.contract_data = data

        if self.many:
            data = self._load_many(data, context)
        else:
            data = self._load_single(data, context)

        context.contract = previous_contract
        context.contract_data = previous_contract_data

        return data

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
            field_names -= set(self.exclude)

        for field_name, field in self._declared_fields.items():
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
        cdef dict d

        if isinstance(data, dict):
            d = <dict>data
            return d.get(field_name, missing)

        return getattr(data, field_name, missing)

    cdef inline object _dump_many(self, object data, Context context):
        if self._hooks[PRE_DUMP_MANY_INDEX] == 1:
            data = self._pre_dump_many(data, context)

        cdef list items = []

        for item in data:
            context.contract_data = item

            items.append(self._dump_single(item, context))

        if self._hooks[POST_DUMP_MANY_INDEX] == 1:
            items = self._post_dump_many(items, context)

        return items

    @cython.boundscheck(False)
    cdef inline object _dump_single(self, object data, Context context):
        if self._hooks[PRE_DUMP_INDEX] == 1:
            data = self._pre_dump(data, context)

        cdef dict result = dict()

        cdef Field field
        cdef object raw, value

        cdef int count = len(self._dump_fields)

        for i in range(count):
            field = self._dump_fields[i]

            raw = self._get_value(data, field.name)

            value = field.dump(raw, context)

            if value is not missing:
                result[field.dump_to] = value

        if self._hooks[POST_DUMP_INDEX] == 1:
            result = self._post_dump(result, context)

        return result

    cdef inline object _load_many(self, object data, Context context):
        if self._hooks[PRE_LOAD_MANY_INDEX] == 1:
            try:
                data = self._pre_load_many(data, context)
            except ValidationError as err:
                raise ContractError([err])

        cdef list items = []

        for item in data:
            items.append(self._load_single(item, context))

        if self._hooks[POST_LOAD_MANY_INDEX] == 1:
            try:
                items = self._post_load_many(items, context)
            except ValidationError as err:
                raise ContractError([err])

        return items

    @cython.boundscheck(False)
    cdef inline object _load_single(self, object data, Context context):
        if self._hooks[PRE_LOAD_INDEX] == 1:
            try:
                data = self._pre_load(data, context)
            except ValidationError as err:
                raise ContractError([err])

        cdef ContractError errors = None
        cdef dict result = dict()
        cdef list load_fields = self._load_fields
        cdef int count = len(load_fields)

        cdef Field field
        cdef object raw, value

        for i in range(count):
            field = load_fields[i]

            try:
                raw = self._get_value(data, field.load_from)

                if self.partial and raw is missing:
                    continue

                value = field.load(raw, context)

                if value is not missing:
                    result[field.name] = value
            except ValidationError as err:
                if not err.field_names:
                    err.field_names = [field.name]

                if errors is None:
                    errors = ContractError([err])
                else:
                    errors.add_error(err)

        if errors:
            raise errors

        if self._hooks[POST_LOAD_INDEX] == 1:
            try:
                result = self._post_load(result, context)
            except ValidationError as err:
                raise ContractError([err])

        return result

    cpdef object _pre_dump(self, object data, Context context):
        return data

    cpdef object _pre_dump_many(self, object data, Context context):
        return data

    cpdef object _pre_load(self, object data, Context context):
        return data

    cpdef object _pre_load_many(self, object data, Context context):
        return data

    cpdef object _post_dump(self, object data, Context context):
        return data

    cpdef object _post_dump_many(self, object data, Context context):
        return data

    cpdef object _post_load(self, object data, Context context):
        return data

    cpdef object _post_load_many(self, object data, Context context):
        return data


class ContractMeta(type):
    def __new__(mcs, name, bases, attrs):
        declared_fields = mcs.get_declared_fields(bases, attrs)

        cls = super(ContractMeta, mcs).__new__(mcs, name, bases, attrs)

        for name, field in declared_fields.items():
            field.bind(name, cls)

        cls._declared_fields = declared_fields
        cls._declared_hooks = mcs.get_declared_hooks(bases, attrs)

        return cls

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

    @classmethod
    def get_declared_hooks(mcs, bases, attrs):
        hooks = [HOOK_DISABLED] * HOOKS_COUNT

        for index, hook_name in enumerate(HOOK_NAMES):
            if attrs.get(hook_name):
                hooks[index] = 1

        for base in reversed(bases):
            # do not consider the BaseContract
            # because the hook methods are defined in there.
            if base is BaseContract:
                continue

            if hasattr(base, '_declared_hooks'):
                for index, value in enumerate(base._declared_hooks):
                    if value == HOOK_ENABLED:
                        hooks[index] = HOOK_ENABLED

        return hooks


class Contract(BaseContract, metaclass=ContractMeta):
    pass

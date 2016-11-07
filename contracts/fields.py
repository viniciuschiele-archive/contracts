"""
Provides a set of classes to serialize Python objects.
"""

from . import utils
from .exceptions import ValidationError
from .utils import formatting, missing
from .validators import LengthValidator, RangeValidator


MISSING_ERROR_MESSAGE = 'ValidationError raised by `{class_name}`, but error key `{key}` does ' \
                        'not exist in the `error_messages` dictionary.'


class Field(object):
    default_error_messages = {
        'required': 'This field is required.',
        'null': 'This field may not be null.',
        'validator_failed': 'Invalid value.'
    }

    def __init__(self, dump_only=False, load_only=False, required=None, default=missing, allow_none=None,
                 dump_to=None, load_from=None, error_messages=None, validators=None):
        self.dump_only = dump_only
        self.load_only = load_only
        self.default = default
        self.allow_none = allow_none
        self.dump_to = dump_to
        self.load_from = load_from
        self.validators = validators or []

        # If `required` is unset, then use `True` unless a default is provided.
        if required is None:
            self.required = default is missing
        else:
            self.required = required

        if allow_none is None:
            self.allow_none = default is None
        else:
            self.allow_none = allow_none

        # Collect default error message from self and parent classes
        messages = {}
        for cls in reversed(self.__class__.__mro__):
            messages.update(getattr(cls, 'default_error_messages', {}))
        messages.update(error_messages or {})
        self.error_messages = messages

        self.field_name = None
        self.parent = None

    def bind(self, field_name, parent):
        self.field_name = field_name
        self.parent = parent

        if not self.dump_to:
            self.dump_to = field_name

        if not self.load_from:
            self.load_from = field_name

    def get_default(self):
        if self.default is missing:
            return missing

        if callable(self.default):
            return self.default()

        return self.default

    def dump(self, value):
        if value is missing:
            return self.get_default()

        if value is None:
            return None

        return self._dump(value)

    def load(self, value):
        if value is missing:
            if getattr(self.root, 'partial', False):
                return missing

            if self.required:
                self._fail('required')

            return self.get_default()

        if value is None:
            if self.allow_none:
                return None
            self._fail('null')

        validated_value = self._load(value)
        self._validate(validated_value)
        return validated_value

    @property
    def root(self):
        """
        Returns the top-level serializer for this field.
        """
        root = getattr(self, '_cached_root')
        if root:
            return root

        root = self
        while root.parent is not None:
            root = root.parent

        setattr(self, '_cached_root', root)

        return root

    def _dump(self, value):
        raise NotImplementedError()

    def _load(self, value):
        raise NotImplementedError()

    def _fail(self, key, **kwargs):
        try:
            message = self.error_messages[key]
            message = formatting.format_error_message(message, **kwargs)
            if isinstance(message, dict):
                raise ValidationError(**message)
            raise ValidationError(message)
        except KeyError:
            class_name = self.__class__.__name__
            message = formatting.format_error_message(MISSING_ERROR_MESSAGE, class_name=class_name, key=key)
            raise AssertionError(message)

    def _validate(self, value):
        errors = []
        for validator in self.validators:
            try:
                if validator(value) is False:
                    self._fail('validator_failed')
            except ValidationError as err:
                if isinstance(err.message, dict):
                    raise

                errors.append(err)

        if errors:
            raise ValidationError(errors)

    # def __deepcopy__(self, memo):
    #     return copy.copy(self)


class IntegerField(Field):
    default_error_messages = {
        'invalid': 'A valid integer is required.',
        'max_value': 'Must be at most {max_value}.',
        'min_value': 'Must be at least {min_value}.'
    }

    def __init__(self, min_value=None, max_value=None, **kwargs):
        super().__init__(**kwargs)
        self.min_value = min_value
        self.max_value = max_value

        if self.min_value is not None or self.max_value is not None:
            self.validators.append(RangeValidator(min_value, max_value, self.error_messages))

    def _load(self, value):
        try:
            return int(value)
        except (ValueError, TypeError):
            self._fail('invalid')

    def _dump(self, value):
        return int(value)


class StringField(Field):
    default_error_messages = {
        'blank': 'This field may not be blank.',
        'max_length': 'Longer than maximum length {max_length}.',
        'min_length': 'Shorter than minimum length {min_length}.'
    }

    def __init__(self, allow_blank=False, trim_whitespace=True, min_length=None, max_length=None, **kwargs):
        super().__init__(**kwargs)
        self.allow_blank = allow_blank
        self.trim_whitespace = trim_whitespace
        self.min_length = min_length
        self.max_length = max_length

        if self.min_length is not None or self.max_length is not None:
            self.validators.append(
                LengthValidator(self.min_length, self.max_length, error_messages=self.error_messages))

    def _load(self, value):
        value = str(value)

        if self.trim_whitespace:
            value = value.strip()

        if value == '' and not self.allow_blank:
            if self.allow_none:
                return None
            self._fail('blank')

        return value

    def _dump(self, value):
        return str(value)


class ContractMeta(type):
    def __new__(mcs, name, bases, attrs):
        declared_fields = mcs.get_declared_fields(bases, attrs)

        cls = super(ContractMeta, mcs).__new__(mcs, name, bases, attrs)

        cls._declared_fields = declared_fields

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


class Contract(Field, metaclass=ContractMeta):
    default_error_messages = {
        'invalid': 'Invalid data. Expected a dictionary, but got {datatype}.'
    }

    def __init__(self, many=False, only=None, partial=False, *args, **kwargs):
        super().__init__(*args, **kwargs)

        only = only or ()
        if not isinstance(only, (list, tuple)):
            raise AssertionError('`only` has to be a list or tuple')

        self.many = many
        self.only = only or ()
        self.partial = partial
        # self.fields = copy.deepcopy(self._declared_fields)
        self.fields = self._declared_fields

        if self.only:
            field_names = set(self.only)
        else:
            field_names = set(self.fields)

        self._load_fields = []
        self._dump_fields = []

        for field_name, field in self.fields.items():
            field.bind(field_name, self)

            if field.field_name in field_names:
                if field.load_only:
                    self._load_fields.append(field)
                elif field.dump_only:
                    self._dump_fields.append(field)
                else:
                    self._dump_fields.append(field)
                    self._load_fields.append(field)

    def pre_dump(self, data):
        return data

    def pre_dump_many(self, data):
        return data

    def pre_load(self, data):
        return data

    def pre_load_many(self, data):
        return data

    def post_dump(self, data, original_data):
        return data

    def post_dump_many(self, data, original_data):
        return data

    def post_load(self, data, original_data):
        return data

    def post_load_many(self, data, original_data):
        return data

    def post_validate(self, data):
        pass

    def _get_value(self, data, field_name):
        if isinstance(data, dict):
            return data.get(field_name, missing)

        return getattr(data, field_name, missing)

    def _dump(self, data):
        if self.many:
            return self._dump_many(data)
        else:
            return self._dump_single(data)

    def _dump_many(self, data):
        items = []

        for item in data:
            items.append(self._dump_single(item))

        return items

    def _dump_single(self, data):
        result = dict()

        data = self.pre_dump(data)

        for field in self._dump_fields:
            raw = self._get_value(data, field.field_name)

            value = field.dump(raw)

            if value is not missing:
                result[field.dump_to] = value

        return self.post_dump(result, data)

    def _load(self, data):
        if self.many:
            return self._load_many(data)
        else:
            return self._load_single(data)

    def _load_many(self, data):
        data = self.pre_load_many(data)

        items = []

        for item in data:
            items.append(self._load_single(item))

        items = self.post_load_many(items, data)

        return items

    def _load_single(self, data):
        if not isinstance(data, dict):
            self._fail('invalid', datatype=type(data).__name__)

        data = self.pre_load(data)

        result = dict()
        errors = dict()

        for field in self._load_fields:
            try:
                raw = self._get_value(data, field.load_from)

                value = field.load(raw)

                if value is not missing:
                    result[field.field_name] = value
            except ValidationError as err:
                errors[field.field_name] = err

        if errors:
            raise ValidationError(errors)

        return self.post_load(result, data)

    def _validate(self, value):
        errors = []

        try:
            super()._validate(value)
        except ValidationError as err:
            errors.append(err)

        try:
            self.post_validate(value)
        except ValidationError as err:
            errors.append(err)

        d = {}

        for error in errors:
            if isinstance(error.message, dict):
                d.update(error.message)
            else:
                d['_contract'] = error

        if d:
            raise ValidationError(d)

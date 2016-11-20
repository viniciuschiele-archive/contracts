"""
Provides a set of classes to serialize Python objects.
"""

cimport cython
import ciso8601
import datetime
import uuid

from . cimport abc
from . cimport validators
from .exceptions cimport ValidationError
from .utils cimport missing

MISSING_ERROR_MESSAGE = 'ValidationError raised by `{class_name}`, but error key `{key}` does ' \
                        'not exist in the `error_messages` dictionary.'


cdef class Field(abc.Field):
    default_error_messages = {
        'required': 'This field is required.',
        'null': 'This field may not be null.',
        'validator_failed': 'Invalid value.'
    }

    def __init__(self, bint dump_only=False, bint load_only=False, required=None, object default=missing, allow_none=None,
                 str dump_to=None, str load_from=None, dict error_messages=None, list validators=None):
        self.dump_only = dump_only
        self.load_only = load_only
        self.default_ = default
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

        self.name = None
        self.parent = None
        self._decorator_validators = []

    cpdef bind(self, str name, abc.Contract parent):
        self.name = name
        self.parent = parent

        if not self.dump_to:
            self.dump_to = name

        if not self.load_from:
            self.load_from = name

        for validator in self._decorator_validators:
            self.validators.append(getattr(parent, validator))

    cpdef object dump(self, object value):
        if value is missing:
            return self._get_default()

        if value is None:
            return None

        return self._dump(value)

    cpdef object load(self, object value):
        if value is None:
            if self.allow_none:
                return None
            self._fail('null')

        if value is missing:
            if self.required:
                self._fail('required')

            return self._get_default()

        validated_value = self._load(value)
        self._validate(validated_value)
        return validated_value

    cpdef validator(self, func):
        self._decorator_validators.append(func.__name__)
        return func

    cpdef _get_default(self):
        if self.default_ is missing:
            return missing

        if callable(self.default_):
            return self.default_()

        return self.default_

    cpdef object _dump(self, object value):
        return value

    cpdef object _load(self, object value):
        return value

    def _fail(self, key, **kwargs):
        try:
            message = self.error_messages[key]
            if kwargs:
                message = message.format(**kwargs)
            raise ValidationError(message)
        except KeyError:
            class_name = self.__class__.__name__
            message = MISSING_ERROR_MESSAGE.format(class_name=class_name, key=key)
            raise AssertionError(message)

    cpdef _validate(self, object value):
        errors = []

        for validator in self.validators:
            try:
                if validator(value) is False:
                    self._fail('validator_failed')
            except ValidationError as err:
                if isinstance(err.messages, dict):
                    errors.append(err.messages)
                else:
                    errors.extend(err.messages)

        if errors:
            raise ValidationError(errors)


cdef class Boolean(Field):
    default_error_messages = {
        'invalid': '"{value}" is not a valid boolean.'
    }

    TRUE_VALUES = {'t', 'T', 'true', 'True', 'TRUE', '1', 1, True}
    FALSE_VALUES = {'f', 'F', 'false', 'False', 'FALSE', '0', 0, 0.0, False}

    cpdef object _load(self, object value):
        if isinstance(value, bool):
            return value

        try:
            if value in self.TRUE_VALUES:
                return True

            if value in self.FALSE_VALUES:
                return False
        except TypeError:
            pass

        self._fail('invalid', value=value)

    cpdef object _dump(self, object value):
        if isinstance(value, bool):
            return value

        if value in self.TRUE_VALUES:
            return True

        if value in self.FALSE_VALUES:
            return False

        return bool(value)


cdef class Date(Field):
    default_error_messages = {
        'invalid': 'Date has wrong format.',
    }

    cpdef object _load(self, object value):
        if isinstance(value, datetime.datetime):
            return value.date()

        if isinstance(value, datetime.date):
            return value

        try:
            parsed = ciso8601.parse_datetime_unaware(value)
            if parsed is not None:
                return parsed
        except (ValueError, TypeError):
            pass

        self._fail('invalid')

    cpdef object _dump(self, object value):
        if isinstance(value, datetime.datetime):
            return value.date().isoformat()

        return value.isoformat()


cdef class DateTime(Field):
    default_error_messages = {
        'invalid': 'Datetime has wrong format.',
        'date': 'Expected a datetime but got a date.',
    }

    cpdef object _load(self, object value):
        if isinstance(value, datetime.datetime):
            return value

        if isinstance(value, datetime.date):
            self._fail('date')

        try:

            parsed = ciso8601.parse_datetime(value)
            if parsed is not None:
                return parsed
        except (ValueError, TypeError):
            pass

        self._fail('invalid')

    cpdef object _dump(self, object value):
        return value.isoformat()


cdef class Float(Field):
    default_error_messages = {
        'invalid': 'A valid number is required.',
        'max_value': 'Ensure this value is less than or equal to {max_value}.',
        'min_value': 'Ensure this value is greater than or equal to {min_value}.',
    }

    def __init__(self, min_value=None, max_value=None, **kwargs):
        super().__init__(**kwargs)
        self.min_value = min_value
        self.max_value = max_value

        if self.min_value is not None or self.max_value is not None:
            self.validators.append(validators.Range(min_value, max_value, self.error_messages))

    cpdef object _load(self, object value):
        if isinstance(value, float):
            return value

        try:
            return float(value)
        except (TypeError, ValueError):
            self._fail('invalid')

    cpdef object _dump(self, object value):
        if isinstance(value, float):
            return value

        return float(value)


cdef class Integer(Field):
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
            self.validators.append(validators.Range(min_value, max_value, self.error_messages))

    cpdef object _load(self, object value):
        if isinstance(value, int):
            return value

        try:
            return int(value)
        except (ValueError, TypeError):
            self._fail('invalid')

    cpdef object _dump(self, object value):
        if isinstance(value, int):
            return value

        return int(value)


cdef class List(Field):
    default_error_messages = {
        'invalid': 'Not a valid list.',
        'empty': 'This list may not be empty.'
    }

    def __init__(self, abc.Field child, bint allow_empty=True, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.child = child
        self.allow_empty = allow_empty

    cpdef object _load(self, object value):
        """
        List of dicts of native values <- List of dicts of primitive datatypes.
        """
        if not isinstance(value, list):
            self._fail('invalid')

        if not self.allow_empty and len(value) == 0:
            self._fail('empty')

        result = []
        errors = {}

        for idx, item in enumerate(value):
            try:
                result.append(self.child.load(item))
            except ValidationError as e:
                errors.update({idx: e.messages})

        if errors:
            raise ValidationError(errors)

        return result

    cpdef object _dump(self, object value):
        """
        List of object instances -> List of dicts of primitive datatypes.
        """
        return [self.child.dump(item) for item in value]


cdef class Method(Field):
    def __init__(self, str dump_method_name=None, str load_method_name=None, **kwargs):
        super(Method, self).__init__(**kwargs)

        self.dump_method_name = dump_method_name
        self.load_method_name = load_method_name

    cpdef object _dump(self, object value):
        if not self.dump_method_name:
            return missing

        method = getattr(self.parent, self.dump_method_name)

        return method(value)

    cpdef object _load(self, object value):
        if not self.load_method_name:
            return missing

        method = getattr(self.parent, self.load_method_name)

        return method(value)


cdef class Nested(Field):
    def __init__(self, nested, bint many=False, set only=None, set exclude=None, **kwargs):
        super(Nested, self).__init__(**kwargs)
        self.nested = nested
        self.many = many
        self.only = only
        self.exclude = exclude

        self._instance = None

    cpdef bind(self, str name, abc.Contract parent):
        super(Nested, self).bind(name, parent)

        self._instance = self.nested(many=self.many, only=self.only, exclude=self.exclude)

    cpdef object _load(self, object value):
        return self._instance.load(value)

    cpdef object _dump(self, object value):
        return self._instance.dump(value)


cdef class String(Field):
    default_error_messages = {
        'blank': 'This field may not be blank.',
        'max_length': 'Longer than maximum length {max_length}.',
        'min_length': 'Shorter than minimum length {min_length}.'
    }

    def __init__(self, bint allow_blank=False, bint trim_whitespace=False, min_length=None, max_length=None, **kwargs):
        super().__init__(**kwargs)
        self.allow_blank = allow_blank
        self.trim_whitespace = trim_whitespace
        self.min_length = min_length
        self.max_length = max_length

        if self.min_length is not None or self.max_length is not None:
            self.validators.append(
                validators.Length(self.min_length, self.max_length, error_messages=self.error_messages))

    cpdef object _load(self, object value):
        if not isinstance(value, str):
            value = str(value)

        if self.trim_whitespace:
            value = value.strip()

        if not self.allow_blank and value == '':
            if self.allow_none:
                return None
            self._fail('blank')

        return value

    cpdef object _dump(self, object value):
        if isinstance(value, str):
            return value
        return str(value)


cdef class UUID(Field):
    default_error_messages = {
        'invalid': '"{value}" is not a valid UUID.',
    }

    cpdef object _load(self, object value):
        if isinstance(value, uuid.UUID):
            return value

        try:
            return uuid.UUID(hex=value)
        except (AttributeError, ValueError):
            self._fail('invalid', value=value)

    @cython.boundscheck(False)
    cpdef object _dump(self, object value):
        cdef str hex = '%032x' % value.int
        return hex[:8] + '-' + hex[8:12] + '-' + hex[12:16] + '-' + hex[16:20] + '-' + hex[20:]

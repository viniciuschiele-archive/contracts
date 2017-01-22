import uuid

from contracts import Contract, Context, fields, timezone
from contracts.exceptions import ValidationError
from contracts.utils import missing
from datetime import datetime, date
from unittest import TestCase


class BaseTestCase(TestCase):
    def _dump_equal(self, field, input_value, expected_value):
        self.assertEqual(expected_value, field.dump(input_value, Context()))

    def _dump_raises(self, field, input_value, expected_failure):
        with self.assertRaises(Exception) as exc_info:
            field.dump(input_value, Context())
        self.assertEqual(expected_failure, str(exc_info.exception))

    def _load_equal(self, field, input_value, expected_value):
        self.assertEqual(expected_value, field.load(input_value, Context()))

    def _load_raises(self, field, input_value, expected_failure):
        with self.assertRaises(Exception) as exc_info:
            field.load(input_value, Context())

        if isinstance(exc_info.exception, ValidationError):
            self.assertEqual(expected_failure, exc_info.exception.messages)
        else:
            self.assertEqual(expected_failure, str(exc_info.exception))


class TestField(BaseTestCase):
    """
    Valid and invalid values for `Field`.
    """
    def test_default(self):
        field = fields.Field(default=123)
        self._load_equal(field, missing, 123)

    def test_callable_default(self):
        field = fields.Field(default=lambda: 123)
        self._load_equal(field, missing, 123)

    def test_bypass_default_on_loading(self):
        field = fields.Field(default=123)
        self._load_equal(field, 456, 456)

    def test_required(self):
        field = fields.Field(required=True)
        self._load_raises(field, missing, ['This field is required.'])
        self._load_equal(field, 'abc', 'abc')

    def test_non_required(self):
        field = fields.Field(required=False)
        self._load_equal(field, missing, missing)
        self._load_equal(field, 'abc', 'abc')

    def test_allow_none(self):
        field = fields.Field(allow_none=True)
        self._load_equal(field, None, None)

    def test_disallow_none(self):
        field = fields.Field(allow_none=False)
        self._load_raises(field, None, ['This field may not be null.'])

    def test_bind(self):
        class Parent(Contract):
            pass

        field = fields.Field()
        field.bind('field1', Parent)

        self.assertEqual(field.dump_to, 'field1')
        self.assertEqual(field.load_from, 'field1')
        self.assertEqual(field.name, 'field1')
        self.assertEqual(field.parent, Parent)

    def test_bind_with_invalid_name(self):
        class Parent(Contract):
            pass

        field = fields.Field()
        self.assertRaises(ValueError, field.bind, None, Parent)
        self.assertRaises(ValueError, field.bind, '', Parent)

    def test_bind_with_invalid_parent(self):
        class InvalidContract:
            pass

        field = fields.Field()
        self.assertRaises(ValueError, field.bind, 'field1', None)
        self.assertRaises(ValueError, field.bind, 'field1', '')
        self.assertRaises(ValueError, field.bind, 'field1', 1)
        self.assertRaises(ValueError, field.bind, 'field1', InvalidContract)

    def test_validator(self):
        def validator(value):
            pass

        field = fields.Field(validators=[validator])
        self._load_equal(field, 123, 123)

    def test_validator_returning_true(self):
        def validator(value):
            return True

        field = fields.Field(validators=[validator])
        self._load_equal(field, 123, 123)

    def test_validator_returning_false(self):
        def validator(value):
            return False

        field = fields.Field(validators=[validator])
        self._load_raises(field, 123, ['Invalid value.'])

    def test_validator_raising_error(self):
        def validator(value):
            raise ValueError()

        field = fields.Field(validators=[validator])
        self.assertRaises(ValueError, field.load, 123, None)

    def test_null_error_message(self):
        field = fields.Field()

        with self.assertRaises(ValidationError) as e:
            field._fail('null')

        self.assertEqual(e.exception.messages, ['This field may not be null.'])

    def test_not_found_error_message(self):
        field = fields.Field()

        with self.assertRaises(AssertionError) as e:
            field._fail('not_found')

    def test_custom_error_message(self):
        field = fields.Field(error_messages={'custom': 'custom fail'})

        with self.assertRaises(ValidationError) as e:
            field._fail('custom')

        self.assertEqual(e.exception.messages, ['custom fail'])

    def test_dict_error_message(self):
        field = fields.Field(error_messages={'invalid': {'message': 'error message', 'code': 123}})

        with self.assertRaises(ValidationError) as e:
            field._fail('invalid')

        self.assertEqual(e.exception.messages, [{'message': 'error message', 'code': 123}])


class TestBoolean(BaseTestCase):
    """
    Valid and invalid values for `Boolean`.
    """
    def test_valid_inputs(self):
        field = fields.Boolean()

        for value in ('True', 'true', 'TRUE', '1', 1, True):
            self._load_equal(field, value, True)

        for value in ('False', 'false', 'FALSE', '0', 0, False):
            self._load_equal(field, value, False)

    def test_invalid_inputs(self):
        self._load_raises(fields.Boolean(), 'foo', ['"foo" is not a valid boolean.'])
        self._load_raises(fields.Boolean(), [], ['"[]" is not a valid boolean.'])

    def test_valid_outputs(self):
        field = fields.Boolean()

        for value in ('True', 'true', 'TRUE', '1', 'other', 1, True):
            self._dump_equal(field, value, True)

        for value in ('False', 'false', 'FALSE', '0', 0, False):
            self._dump_equal(field, value, False)

    def test_invalid_outputs(self):
        field = fields.Boolean()
        self._dump_raises(field, [], "unhashable type: 'list'")
        self._dump_raises(field, {}, "unhashable type: 'dict'")


class TestDate(BaseTestCase):
    """
    Valid and invalid values for `Date`.
    """
    def test_valid_inputs(self):
        field = fields.Date()
        self._load_equal(field, '2001-01', date(2001, 1, 1))
        self._load_equal(field, '2001-01-20', date(2001, 1, 20))
        self._load_equal(field, '20010120', date(2001, 1, 20))
        self._load_equal(field, '2001-01-20T01:00:00', date(2001, 1, 20))
        self._load_equal(field, date(2001, 1, 20), date(2001, 1, 20))
        self._load_equal(field, datetime(2001, 1, 20, 12, 00), date(2001, 1, 20))

    def test_invalid_inputs(self):
        field = fields.Date()
        self._load_raises(field, '', ['Date has wrong format.'])
        self._load_raises(field, 'abc', ['Date has wrong format.'])
        self._load_raises(field, '2001-13-01', ['Date has wrong format.'])
        self._load_raises(field, '2001-01-32', ['Date has wrong format.'])
        self._load_raises(field, 20010120, ['Date has wrong format.'])

    def test_valid_outputs(self):
        field = fields.Date()
        self._dump_equal(field, date(2001, 1, 20), '2001-01-20')
        self._dump_equal(field, datetime(2001, 1, 20, 12, 00), '2001-01-20')

    def test_invalid_outputs(self):
        field = fields.Date()
        self._dump_raises(field, '2001-01-20', "'str' object has no attribute 'isoformat'")
        self._dump_raises(field, 'abc',  "'str' object has no attribute 'isoformat'")
        self._dump_raises(field, 1, "'int' object has no attribute 'isoformat'")


class TestDateTime(BaseTestCase):
    """
    Valid and invalid values for `DateTime`.
    """

    def test_valid_inputs(self):
        field = fields.DateTime()
        self._load_equal(field, '2001-01-01', datetime(2001, 1, 1))
        self._load_equal(field, '2001-01-01 13:00', datetime(2001, 1, 1, 13, 00))
        self._load_equal(field, '2001-01-01T13:00:01', datetime(2001, 1, 1, 13, 0, 1))
        self._load_equal(field, '2001-01-01T13:00:01.001', datetime(2001, 1, 1, 13, 0, 1, 1000))
        self._load_equal(field, '2001-01-01T13:00Z', datetime(2001, 1, 1, 13, 00))
        self._load_equal(field, '2001-01-01T13:00+00:00', datetime(2001, 1, 1, 13, 00))
        self._load_equal(field, datetime(2001, 1, 1, 13, 00), datetime(2001, 1, 1, 13, 00))
        self._load_equal(field, datetime(2001, 1, 1, 13, 00, tzinfo=timezone.utc), datetime(2001, 1, 1, 13, 00))

    def test_valid_inputs_with_default_timezone(self):
        field = fields.DateTime(default_timezone=timezone.utc)
        self._load_equal(field, '2001-01-01', datetime(2001, 1, 1, tzinfo=timezone.utc))
        self._load_equal(field, '2001-01-01 13:00', datetime(2001, 1, 1, 13, 00, tzinfo=timezone.utc))
        self._load_equal(field, '2001-01-01T13:00', datetime(2001, 1, 1, 13, 00, tzinfo=timezone.utc))
        self._load_equal(field, '2001-01-01T13:00Z', datetime(2001, 1, 1, 13, 00, tzinfo=timezone.utc))
        self._load_equal(field, '2001-01-01T13:00+00:00', datetime(2001, 1, 1, 13, 00, tzinfo=timezone.utc))
        self._load_equal(field, datetime(2001, 1, 1, 13, 00), datetime(2001, 1, 1, 13, 00, tzinfo=timezone.utc))
        self._load_equal(field, datetime(2001, 1, 1, 13, 00, tzinfo=timezone.utc), datetime(2001, 1, 1, 13, 00, tzinfo=timezone.utc))

    def test_invalid_inputs(self):
        field = fields.DateTime()
        self._load_raises(field, '', ['Datetime has wrong format.'])
        self._load_raises(field, 'abc', ['Datetime has wrong format.'])
        self._load_raises(field, '2001-13-01', ['Datetime has wrong format.'])
        self._load_raises(field, '2001-01-32', ['Datetime has wrong format.'])
        # self._load_raises(field, '2001-01-01T99:00', ['Datetime has wrong format.'])
        self._load_raises(field, 20010120, ['Datetime has wrong format.'])
        self._load_raises(field, date(2001, 1, 1), ['Expected a datetime but got a date.'])

    def test_valid_outputs(self):
        field = fields.DateTime()
        self._dump_equal(field, datetime(2001, 1, 1, 13, 00), '2001-01-01T13:00:00')
        self._dump_equal(field, datetime(2001, 1, 1, 13, 00, tzinfo=timezone.utc), '2001-01-01T13:00:00+00:00')

    def test_invalid_outputs(self):
        field = fields.DateTime()
        self._dump_raises(field, '2001-01-01T13:00:00', "'str' object has no attribute 'isoformat'")
        self._dump_raises(field, 123, "'int' object has no attribute 'isoformat'")


class TestFloat(BaseTestCase):
    """
    Valid and invalid values for `Float`.
    """
    def test_valid_inputs(self):
        field = fields.Float()
        self._load_equal(field, '1', 1.0)
        self._load_equal(field, '0', 0.0)
        self._load_equal(field, 1, 1.0)
        self._load_equal(field, 0, 0.0)
        self._load_equal(field, 1.0, 1.0)
        self._load_equal(field, 0.0, 0.0)

    def test_invalid_inputs(self):
        field = fields.Float()
        self._load_raises(field, 'abc', ['A valid number is required.'])

    def test_valid_outputs(self):
        field = fields.Float()
        self._dump_equal(field, '1', 1.0)
        self._dump_equal(field, '0', 0.0)
        self._dump_equal(field, 1, 1.0)
        self._dump_equal(field, 0, 0.0)
        self._dump_equal(field, 1, 1.0)
        self._dump_equal(field, 0, 0.0)

    def test_invalid_outputs(self):
        field = fields.Float()
        self._dump_raises(field, 'abc', "could not convert string to float: 'abc'")
        self._dump_raises(field, [], "float() argument must be a string or a number, not 'list'")


class TestMinMaxFloat(BaseTestCase):
    """
    Valid and invalid values for `Float`.
    """
    def test_valid_inputs(self):
        field = fields.Float(min_value=1, max_value=3)
        self._load_equal(field, 1.0, 1.0)
        self._load_equal(field, 3.0, 3.0)

    def test_invalid_inputs(self):
        field = fields.Float(min_value=1, max_value=3)
        self._load_raises(field, 0.9, ['Ensure this value is greater than or equal to 1.'])
        self._load_raises(field, 3.1, ['Ensure this value is less than or equal to 3.'])

    def test_valid_outputs(self):
        field = fields.Float(min_value=1, max_value=3)
        self._dump_equal(field, 0.0, 0.0)
        self._dump_equal(field, 4.0, 4.0)


class TestFunction(BaseTestCase):
    """
    Valid and invalid values for `Function`.
    """
    def test_dump_func(self):
        def dump_func(value, context):
            return value

        field = fields.Function(dump_func=dump_func)
        self._dump_equal(field, 'value', 'value')

    def test_load_func(self):
        def load_func(value, context):
            return value

        field = fields.Function(load_func=load_func)
        self._load_equal(field, 'value', 'value')

    def test_without_func(self):
        field = fields.Function()
        self._load_equal(field, 'value', missing)
        self._dump_equal(field, 'value', missing)

    def test_func_not_callable(self):
        self.assertRaises(ValueError, fields.Function, dump_func='dump_func')

    def test_func_with_wrong_parameters(self):
        def func(value):
            pass

        field = fields.Function(dump_func=func, load_func=func)
        self._dump_raises(field, 'value', 'func() takes 1 positional argument but 2 were given')
        self._load_raises(field, 'value', 'func() takes 1 positional argument but 2 were given')

    def test_dump_func_passed_is_dump_only(self):
        def func(value, context):
            pass

        field = fields.Function(dump_func=func)
        self.assertEqual(field.dump_only, True)
        self.assertEqual(field.load_only, False)

    def test_load_func_passed_is_load_only(self):
        def func(value, context):
            pass

        field = fields.Function(load_func=func)
        self.assertEqual(field.dump_only, False)
        self.assertEqual(field.load_only, True)


class TestInteger(BaseTestCase):
    """
    Valid and invalid values for `Integer`.
    """
    def test_valid_inputs(self):
        field = fields.Integer()
        self._load_equal(field, '1', 1)
        self._load_equal(field, '0', 0)
        self._load_equal(field, 1, 1)
        self._load_equal(field, 0, 0)
        self._load_equal(field, 1.0, 1)
        self._load_equal(field, 0.0, 0)

    def test_invalid_inputs(self):
        field = fields.Integer()
        self._load_raises(field, 'abc', ['A valid integer is required.'])
        self._load_raises(field, '1.0', ['A valid integer is required.'])

    def test_valid_outputs(self):
        field = fields.Integer()
        self._dump_equal(field, 1, 1)
        self._dump_equal(field, 1.0, 1)
        self._dump_equal(field, '1', 1)

    def test_invalid_outputs(self):
        field = fields.Integer()
        self._dump_raises(field, 'abc', "invalid literal for int() with base 10: 'abc'")
        self._dump_raises(field, [], "int() argument must be a string or a number, not 'list'")


class TestMinMaxInteger(BaseTestCase):
    def test_valid_inputs(self):
        field = fields.Integer(min_value=1, max_value=3)
        self._load_equal(field, 1, 1)
        self._load_equal(field, 3, 3)

    def test_invalid_inputs(self):
        field = fields.Integer(min_value=1, max_value=3)
        self._load_raises(field, 0, ['Must be at least 1.'])
        self._load_raises(field, 4, ['Must be at most 3.'])

    def test_valid_outputs(self):
        field = fields.Integer(min_value=1, max_value=3)
        self._dump_equal(field, 0, 0)
        self._dump_equal(field, 2, 2)
        self._dump_equal(field, 4, 4)


class TestListField(BaseTestCase):
    """
    Values for `List` with Integer as child.
    """
    def test_valid_inputs(self):
        field = fields.List(fields.Integer())
        self._load_equal(field, [], [])
        self._load_equal(field, [1, 2, 3], [1, 2, 3])
        self._load_equal(field, ['1', '2', '3'], [1, 2, 3])
        self._load_equal(field, {1, 2}, [1, 2])
        self._load_equal(field, (1, 2), [1, 2])

    def test_invalid_inputs(self):
        field = fields.List(fields.Integer())
        self._load_raises(field, 'not a list', ['Not a valid list.'])
        self._load_raises(field, [1, 2, 'error'], [{2: ['A valid integer is required.']}])

    def test_valid_outputs(self):
        field = fields.List(fields.Integer())
        self._dump_equal(field, [], [])
        self._dump_equal(field, [1, 2, 3], [1, 2, 3])
        self._dump_equal(field, ['1', '2', '3'], [1, 2, 3])
        self._dump_equal(field, {1, 2, 3}, [1, 2, 3])
        self._dump_equal(field, ('1', '2', '3'), [1, 2, 3])

    def test_disallow_empty(self):
        field = fields.List(fields.Integer(), allow_empty=False)
        self._load_raises(field, [], ['This list may not be empty.'])


class TestMethod(BaseTestCase):
    """
    Valid and invalid values for `Method`.
    """
    def test_dump_method(self):
        class MyContract(Contract):
            def dump_method(self, value, context):
                return value

        field = fields.Method(dump_method_name='dump_method')
        field.bind('field', MyContract)

        self._dump_equal(field, 'value', 'value')

    def test_load_method(self):
        class MyContract(Contract):
            def load_method(self, value, context):
                return value

        field = fields.Method(load_method_name='load_method')
        field.bind('field', MyContract)

        self._load_equal(field, 'value', 'value')

    def test_without_method(self):
        field = fields.Method()
        self._dump_equal(field, 'value', missing)
        self._load_equal(field, 'value', missing)

    def test_method_not_callable(self):
        class MyContract(Contract):
            dump_method = 'attribute'

        field = fields.Method(dump_method_name='dump_method')
        self.assertRaises(ValueError, field.bind, 'field', MyContract)

    def test_method_missing(self):
        class MyContract(Contract):
            dump_method = 'attribute'

        field = fields.Method(load_method_name='not_found')
        self.assertRaises(ValueError, field.bind, 'field', MyContract)

    def test_dump_method_passed_is_dump_only(self):
        field = fields.Method(dump_method_name='method_name')
        self.assertEqual(field.dump_only, True)
        self.assertEqual(field.load_only, False)

    def test_load_method_passed_is_load_only(self):
        field = fields.Method(load_method_name='method_name')
        self.assertEqual(field.dump_only, False)
        self.assertEqual(field.load_only, True)


class TestString(BaseTestCase):
    """
    Valid and invalid values for `String`.
    """
    def test_valid_inputs(self):
        field = fields.String()
        self._load_equal(field, 1, '1')
        self._load_equal(field, 'abc', 'abc')
        self._load_equal(field, ' abc ', ' abc ')

    def test_invalid_inputs(self):
        field = fields.String()
        self._load_raises(field, '', ['This field may not be blank.'])

    def test_valid_outputs(self):
        field = fields.String()
        self._dump_equal(field, 1, '1')
        self._dump_equal(field, 1.0, '1.0')
        self._dump_equal(field, 'abc', 'abc')

    def test_trim_whitespace(self):
        field = fields.String(trim_whitespace=True)
        self._load_equal(field, ' abc ', 'abc')

    def test_trim_whitespace_with_space_value(self):
        field = fields.String(trim_whitespace=True)
        self._load_raises(field, ' ', ['This field may not be blank.'])

    def test_allow_blank(self):
        field = fields.String(allow_blank=True)
        self._load_equal(field, '', '')

    def test_allow_none_with_empty_value(self):
        field = fields.String(allow_none=True)
        self._load_equal(field, '', None)


class TestMinMaxString(BaseTestCase):
    """
    Valid and invalid values for `String` with min and max limits.
    """
    def test_valid_inputs(self):
        field = fields.String(min_length=2, max_length=4)
        self._load_equal(field, 12, '12')
        self._load_equal(field, 1.0, '1.0')
        self._load_equal(field, 'ab', 'ab')
        self._load_equal(field, 'abcd', 'abcd')

    def test_invalid_inputs(self):
        field = fields.String(min_length=2, max_length=4)
        self._load_raises(field, '1', ['Shorter than minimum length 2.'])
        self._load_raises(field, 'abcde', ['Longer than maximum length 4.'])

    def test_valid_outputs(self):
        field = fields.String(min_length=1, max_length=3)
        self._dump_equal(field, '', '')
        self._dump_equal(field, '12345', '12345')


class TestUUID(BaseTestCase):
    """
    Valid and invalid values for `UUID`.
    """
    def test_valid_inputs(self):
        field = fields.UUID()
        self._load_equal(field, '825d7aeb-05a9-45b5-a5b7-05df87923cda', uuid.UUID('825d7aeb-05a9-45b5-a5b7-05df87923cda'))
        self._load_equal(field, '825d7aeb05a945b5a5b705df87923cda', uuid.UUID('825d7aeb-05a9-45b5-a5b7-05df87923cda'))
        self._load_equal(field, uuid.UUID('825d7aeb-05a9-45b5-a5b7-05df87923cda'), uuid.UUID('825d7aeb-05a9-45b5-a5b7-05df87923cda'))

    def test_invalid_inputs(self):
        field = fields.UUID()
        self._load_raises(field, '825d7aeb-05a9-45b5-a5b7', ['"825d7aeb-05a9-45b5-a5b7" is not a valid UUID.'])
        self._load_raises(field, (1, 2, 3), ['"(1, 2, 3)" is not a valid UUID.'])
        self._load_raises(field, 123, ['"123" is not a valid UUID.'])

    def test_valid_outputs(self):
        field = fields.UUID()
        self._dump_equal(field, uuid.UUID('825d7aeb-05a9-45b5-a5b7-05df87923cda'), '825d7aeb-05a9-45b5-a5b7-05df87923cda')

    def test_invalid_outputs(self):
        field = fields.UUID()
        self._dump_raises(field, '825d7aeb-05a9-45b5-a5b7-05df87923cda',  "'str' object has no attribute 'int'")
        self._dump_raises(field, [], "'list' object has no attribute 'int'")

    def test_hex_verbose_format(self):
        field = fields.UUID(dump_format='hex_verbose')
        self._dump_equal(field, uuid.UUID('825d7aeb-05a9-45b5-a5b7-05df87923cda'), '825d7aeb-05a9-45b5-a5b7-05df87923cda')

    def test_hex_format(self):
        field = fields.UUID(dump_format='hex')
        self._dump_equal(field, uuid.UUID('825d7aeb-05a9-45b5-a5b7-05df87923cda'), '825d7aeb05a945b5a5b705df87923cda')

    def test_int_format(self):
        field = fields.UUID(dump_format='int')
        self._dump_equal(field, uuid.UUID('825d7aeb-05a9-45b5-a5b7-05df87923cda'), 173285016134224701509569922458251836634)

    def test_invalid_format(self):
        self.assertRaises(ValueError, fields.UUID, dump_format='invalid')

import uuid

from contracts import Contract, fields, timezone
from contracts.exceptions import ValidationError
from contracts.utils import missing
from datetime import datetime, date
from unittest import TestCase


class TestField(TestCase):
    """
    Valid and invalid values for `Boolean`.
    """
    def test_default(self):
        field = fields.Field(default=123)
        self.assertEqual(field.load(missing), 123)

    def test_callable_default(self):
        field = fields.Field(default=lambda: 123)
        self.assertEqual(field.load(missing), 123)

    def test_bypass_default_on_loading(self):
        field = fields.Field(default=123)
        self.assertEqual(field.load(456), 456)

    def test_required(self):
        field = fields.Field(required=True)
        self.assertRaises(ValidationError, field.load, missing)
        self.assertEqual(field.load('abc'), 'abc')

    def test_non_required(self):
        field = fields.Field(required=False)
        self.assertEqual(field.load(missing), missing)
        self.assertEqual(field.load('abc'), 'abc')

    def test_allow_none(self):
        field = fields.Field(allow_none=True)
        self.assertEqual(field.load(None), None)

    def test_disallow(self):
        field = fields.Field(allow_none=False)
        self.assertRaises(ValidationError, field.load, None)

    def test_bind(self):
        class Parent(Contract):
            pass

        parent = Parent()

        field = fields.Field()
        field.bind('field1', parent)

        self.assertEqual(field.dump_to, 'field1')
        self.assertEqual(field.load_from, 'field1')
        self.assertEqual(field.parent, parent)

    def test_validator(self):
        def validator(value):
            pass

        field = fields.Field(validators=[validator])
        self.assertEqual(field.load(123), 123)

    def test_validator_returning_true(self):
        def validator(value):
            return True

        field = fields.Field(validators=[validator])
        self.assertEqual(field.load(123), 123)

    def test_validator_returning_false(self):
        def validator(value):
            return False

        field = fields.Field(validators=[validator])
        self.assertRaises(ValidationError, field.load, 123)

    def test_validator_raising_error(self):
        def validator(value):
            raise ValueError()

        field = fields.Field(validators=[validator])
        self.assertRaises(ValueError, field.load, 123)

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


class TestBoolean(TestCase):
    """
    Valid and invalid values for `Boolean`.
    """
    def test_valid_inputs(self):
        field = fields.Boolean()

        for value in ('True', 'true', 'TRUE', '1', 1, True):
            self.assertEqual(field.load(value), True)

        for value in ('False', 'false', 'FALSE', '0', 0, False):
            self.assertEqual(field.load(value), False)

    def test_invalid_inputs(self):
        self.assertRaises(ValidationError, fields.Boolean().load, 'foo')
        self.assertRaises(ValidationError, fields.Boolean().load, [])

    def test_valid_outputs(self):
        field = fields.Boolean()

        for value in ('True', 'true', 'TRUE', '1', 'other', 1, True):
            self.assertEqual(field.dump(value), True)

        for value in ('False', 'false', 'FALSE', '0', 0, False):
            self.assertEqual(field.dump(value), False)

    def test_invalid_outputs(self):
        field = fields.Boolean()
        self.assertRaises(TypeError, field.dump, [])
        self.assertRaises(TypeError, field.dump, {})


class TestDate(TestCase):
    """
    Valid and invalid values for `Date`.
    """
    def test_valid_inputs(self):
        field = fields.Date()
        self.assertEqual(field.load('2001-01'), date(2001, 1, 1))
        self.assertEqual(field.load('2001-01-20'), date(2001, 1, 20))
        self.assertEqual(field.load('20010120'), date(2001, 1, 20))
        self.assertEqual(field.load('2001-01-20T01:00:00'), date(2001, 1, 20))
        self.assertEqual(field.load(date(2001, 1, 20)), date(2001, 1, 20))
        self.assertEqual(field.load(datetime(2001, 1, 20, 12, 00)), date(2001, 1, 20))

    def test_invalid_inputs(self):
        field = fields.Date()
        self.assertRaises(ValidationError, field.load, '')
        self.assertRaises(ValidationError, field.load, 'abc')
        self.assertRaises(ValidationError, field.load, '2001-13-01')
        self.assertRaises(ValidationError, field.load, '2001-01-32')
        self.assertRaises(ValidationError, field.load, 20010120)

    def test_valid_outputs(self):
        field = fields.Date()
        self.assertEqual(field.dump(date(2001, 1, 20)), '2001-01-20')
        self.assertEqual(field.dump(datetime(2001, 1, 20, 12, 00)), '2001-01-20')

    def test_invalid_outputs(self):
        field = fields.Date()
        self.assertRaises(AttributeError, field.dump, '2001-01-20')
        self.assertRaises(AttributeError, field.dump, 'abc')


class TestDateTime(TestCase):
    """
    Valid and invalid values for `DateTime`.
    """

    def test_valid_inputs(self):
        field = fields.DateTime()
        self.assertEqual(field.load('2001-01-01'), datetime(2001, 1, 1))
        self.assertEqual(field.load('2001-01-01 13:00'), datetime(2001, 1, 1, 13, 00))
        self.assertEqual(field.load('2001-01-01T13:00:01'), datetime(2001, 1, 1, 13, 0, 1))
        self.assertEqual(field.load('2001-01-01T13:00:01.001'), datetime(2001, 1, 1, 13, 0, 1, 1000))
        self.assertEqual(field.load('2001-01-01T13:00Z'), datetime(2001, 1, 1, 13, 00))
        self.assertEqual(field.load('2001-01-01T13:00+00:00'), datetime(2001, 1, 1, 13, 00))
        self.assertEqual(field.load(datetime(2001, 1, 1, 13, 00)), datetime(2001, 1, 1, 13, 00))
        self.assertEqual(field.load(datetime(2001, 1, 1, 13, 00, tzinfo=timezone.utc)), datetime(2001, 1, 1, 13, 00))

    def test_valid_inputs_with_default_timezone(self):
        field = fields.DateTime(default_timezone=timezone.utc)
        self.assertEqual(field.load('2001-01-01'), datetime(2001, 1, 1, tzinfo=timezone.utc))
        self.assertEqual(field.load('2001-01-01 13:00'), datetime(2001, 1, 1, 13, 00, tzinfo=timezone.utc))
        self.assertEqual(field.load('2001-01-01T13:00'), datetime(2001, 1, 1, 13, 00, tzinfo=timezone.utc))
        self.assertEqual(field.load('2001-01-01T13:00Z'), datetime(2001, 1, 1, 13, 00, tzinfo=timezone.utc))
        self.assertEqual(field.load('2001-01-01T13:00+00:00'), datetime(2001, 1, 1, 13, 00, tzinfo=timezone.utc))
        self.assertEqual(field.load(datetime(2001, 1, 1, 13, 00)), datetime(2001, 1, 1, 13, 00, tzinfo=timezone.utc))
        self.assertEqual(field.load(datetime(2001, 1, 1, 13, 00, tzinfo=timezone.utc)), datetime(2001, 1, 1, 13, 00, tzinfo=timezone.utc))

    def test_invalid_inputs(self):
        field = fields.DateTime()
        self.assertRaises(ValidationError, field.load, '')
        self.assertRaises(ValidationError, field.load, 'abc')
        self.assertRaises(ValidationError, field.load, '2001-13-01')
        self.assertRaises(ValidationError, field.load, '2001-01-32')
        # self.assertRaises(ValidationError, field.load, '2001-01-01T99:00')
        self.assertRaises(ValidationError, field.load, 20010120)
        self.assertRaises(ValidationError, field.load, date(2001, 1, 1))

    def test_valid_outputs(self):
        field = fields.DateTime()
        self.assertEqual(field.dump(datetime(2001, 1, 1, 13, 00)), '2001-01-01T13:00:00')
        self.assertEqual(field.dump(datetime(2001, 1, 1, 13, 00, tzinfo=timezone.utc)), '2001-01-01T13:00:00+00:00')

    def test_invalid_outputs(self):
        field = fields.DateTime()
        self.assertRaises(AttributeError, field.dump, '2001-01-01T13:00:00')
        self.assertRaises(AttributeError, field.dump, 123)


class TestFloat(TestCase):
    """
    Valid and invalid values for `Float`.
    """
    def test_valid_inputs(self):
        field = fields.Float()
        self.assertEqual(field.load('1'), 1.0)
        self.assertEqual(field.load('0'), 0.0)
        self.assertEqual(field.load(1), 1.0)
        self.assertEqual(field.load(0), 0.0)
        self.assertEqual(field.load(1.0), 1.0)
        self.assertEqual(field.load(0.0), 0.0)

    def test_invalid_inputs(self):
        field = fields.Float()
        self.assertRaises(ValidationError, field.load, 'abc')

    def test_valid_outputs(self):
        field = fields.Float()
        self.assertEqual(field.dump('1'), 1.0)
        self.assertEqual(field.dump('0'), 0.0)
        self.assertEqual(field.dump(1), 1.0)
        self.assertEqual(field.dump(0), 0.0)
        self.assertEqual(field.dump(1), 1.0)
        self.assertEqual(field.dump(0), 0.0)

    def test_invalid_outputs(self):
        field = fields.Float()
        self.assertRaises(ValueError, field.dump, 'abc')


class TestMinMaxFloat(TestCase):
    """
    Valid and invalid values for `Float`.
    """
    def test_valid_inputs(self):
        field = fields.Float(min_value=1, max_value=3)
        self.assertEqual(field.load(1.0), 1.0)
        self.assertEqual(field.load(3.0), 3.0)

    def test_invalid_inputs(self):
        field = fields.Float(min_value=1, max_value=3)
        self.assertRaises(ValidationError, field.load, 0.9)
        self.assertRaises(ValidationError, field.load, 3.1)

    def test_valid_outputs(self):
        field = fields.Float(min_value=1, max_value=3)
        self.assertEqual(field.dump(0.0), 0.0)
        self.assertEqual(field.dump(4.0), 4.0)


class TestFunction(TestCase):
    """
    Valid and invalid values for `Function`.
    """
    def test_dump_func(self):
        def dump_func(value):
            return value

        field = fields.Function(dump_func=dump_func)
        self.assertEqual(field.dump('value'), 'value')

    def test_load_func(self):
        def load_func(value):
            return value

        field = fields.Function(load_func=load_func)
        self.assertEqual(field.load('value'), 'value')

    def test_without_func(self):
        field = fields.Function()
        self.assertEqual(field.load('value'), missing)
        self.assertEqual(field.dump('value'), missing)


class TestInteger(TestCase):
    """
    Valid and invalid values for `Integer`.
    """
    def test_valid_inputs(self):
        field = fields.Integer()
        self.assertEqual(field.load('1'), 1)
        self.assertEqual(field.load('0'), 0)
        self.assertEqual(field.load(1), 1)
        self.assertEqual(field.load(0), 0)
        self.assertEqual(field.load(1.0), 1)
        self.assertEqual(field.load(0.0), 0)

    def test_invalid_inputs(self):
        field = fields.Integer()
        self.assertRaises(ValidationError, field.load, 'abc')
        self.assertRaises(ValidationError, field.load, '1.0')

    def test_valid_outputs(self):
        field = fields.Integer()
        self.assertEqual(field.dump(0), 0)
        self.assertEqual(field.dump(4), 4)

    def test_invalid_outputs(self):
        field = fields.Integer()
        self.assertRaises(ValueError, field.dump, 'abc')


class TestMinMaxInteger(TestCase):
    def test_valid_inputs(self):
        field = fields.Integer(min_value=1, max_value=3)
        self.assertEqual(field.load(1), 1)
        self.assertEqual(field.load(3), 3)

    def test_invalid_inputs(self):
        field = fields.Integer(min_value=1, max_value=3)
        self.assertRaises(ValidationError, field.load, 0)
        self.assertRaises(ValidationError, field.load, 4)

    def test_valid_outputs(self):
        field = fields.Integer(min_value=1, max_value=3)
        self.assertEqual(field.dump(0), 0)
        self.assertEqual(field.dump(2), 2)
        self.assertEqual(field.dump(4), 4)


class TestListField(TestCase):
    """
    Values for `List` with Integer as child.
    """
    def test_valid_inputs(self):
        field = fields.List(fields.Integer())
        self.assertEqual(field.load([]), [])
        self.assertEqual(field.load([1, 2, 3]), [1, 2, 3])
        self.assertEqual(field.load(['1', '2', '3']), [1, 2, 3])
        self.assertEqual(field.load({1, 2}), [1, 2])
        self.assertEqual(field.load((1, 2)), [1, 2])

    def test_invalid_inputs(self):
        field = fields.List(fields.Integer())
        self.assertRaises(ValidationError, field.load, 'not a list')
        self.assertRaises(ValidationError, field.load, [1, 2, 'error'])

    def test_valid_outputs(self):
        field = fields.List(fields.Integer())
        self.assertEqual(field.dump([]), [])
        self.assertEqual(field.dump([1, 2, 3]), [1, 2, 3])
        self.assertEqual(field.dump(['1', '2', '3']), [1, 2, 3])
        self.assertEqual(field.dump({1, 2, 3}), [1, 2, 3])
        self.assertEqual(field.dump(('1', '2', '3')), [1, 2, 3])

    def test_disallow_empty(self):
        field = fields.List(fields.Integer(), allow_empty=False)
        self.assertRaises(ValidationError, field.load, [])


class TestMethod(TestCase):
    """
    Valid and invalid values for `Method`.
    """
    def test_dump_func(self):
        class Data(Contract):
            def dump_method(self, value):
                return value

        field = fields.Method(dump_method_name='dump_method')
        field.bind('field', Data())

        self.assertEqual(field.dump('value'), 'value')

    def test_load_func(self):
        class Data(Contract):
            def load_method(self, value):
                return value

        field = fields.Method(load_method_name='load_method')
        field.bind('field', Data())

        self.assertEqual(field.load('value'), 'value')

    def test_without_methods(self):
        field = fields.Method()
        self.assertEqual(field.dump('value'), missing)
        self.assertEqual(field.load('value'), missing)

    def test_not_callable_methods(self):
        class Data(Contract):
            dump_method = 'attribute'

        field = fields.Method(dump_method_name='dump_method')
        self.assertRaises(ValueError, field.bind, 'field', Data())

        field = fields.Method(load_method_name='not_found')
        self.assertRaises(ValueError, field.bind, 'field', Data())


class TestString(TestCase):
    """
    Valid and invalid values for `String`.
    """
    def test_valid_inputs(self):
        field = fields.String()
        self.assertEqual(field.load(1), '1')
        self.assertEqual(field.load('abc'), 'abc')
        self.assertEqual(field.load(' abc '), ' abc ')

    def test_invalid_inputs(self):
        field = fields.String()
        self.assertRaises(ValidationError, field.load, '')

    def test_valid_outputs(self):
        field = fields.String()
        self.assertEqual(field.dump(1), '1')
        self.assertEqual(field.dump(1.0), '1.0')
        self.assertEqual(field.dump('abc'), 'abc')

    def test_trim_whitespace(self):
        field = fields.String(trim_whitespace=True)
        self.assertEqual(field.load(' abc '), 'abc')

    def test_trim_whitespace_with_space_value(self):
        field = fields.String(trim_whitespace=True)
        self.assertRaises(ValidationError, field.load, ' ')

    def test_allow_blank(self):
        field = fields.String(allow_blank=True)
        self.assertEqual(field.load(''), '')

    def test_allow_none_with_empty_value(self):
        field = fields.String(allow_none=True)
        self.assertEqual(field.load(''), None)


class TestMinMaxString(TestCase):
    """
    Valid and invalid values for `String` with min and max limits.
    """
    def test_valid_inputs(self):
        field = fields.String(min_length=2, max_length=4)
        self.assertEqual(field.load(12), '12')
        self.assertEqual(field.load(1.0), '1.0')
        self.assertEqual(field.load('ab'), 'ab')
        self.assertEqual(field.load('abcd'), 'abcd')

    def test_invalid_inputs(self):
        field = fields.String(min_length=2, max_length=4)
        self.assertRaises(ValidationError, field.load, '1')
        self.assertRaises(ValidationError, field.load, 1)
        self.assertRaises(ValidationError, field.load, 'abcde')
        self.assertRaises(ValidationError, field.load, '12345')

    def test_valid_outputs(self):
        field = fields.String(min_length=1, max_length=3)
        self.assertEqual(field.dump(''), '')
        self.assertEqual(field.dump('12345'), '12345')


class TestUUID(TestCase):
    """
    Valid and invalid values for `UUID`.
    """
    def test_valid_inputs(self):
        field = fields.UUID()
        self.assertEqual(field.load('825d7aeb-05a9-45b5-a5b7-05df87923cda'), uuid.UUID('825d7aeb-05a9-45b5-a5b7-05df87923cda'))
        self.assertEqual(field.load('825d7aeb05a945b5a5b705df87923cda'), uuid.UUID('825d7aeb-05a9-45b5-a5b7-05df87923cda'))
        self.assertEqual(field.load(uuid.UUID('825d7aeb-05a9-45b5-a5b7-05df87923cda')), uuid.UUID('825d7aeb-05a9-45b5-a5b7-05df87923cda'))

    def test_invalid_inputs(self):
        field = fields.UUID()
        self.assertRaises(ValidationError, field.load, '825d7aeb-05a9-45b5-a5b7')
        self.assertRaises(ValidationError, field.load, (1, 2, 3))
        self.assertRaises(ValidationError, field.load, 123)

    def test_valid_outputs(self):
        field = fields.UUID()
        self.assertEqual(field.dump(uuid.UUID('825d7aeb-05a9-45b5-a5b7-05df87923cda')), '825d7aeb-05a9-45b5-a5b7-05df87923cda')

    def test_invalid_outputs(self):
        field = fields.UUID()
        self.assertRaises(AttributeError, field.dump, '825d7aeb-05a9-45b5-a5b7-05df87923cda')

    def test_hex_verbose_format(self):
        field = fields.UUID(dump_format='hex_verbose')
        self.assertEqual(field.dump(uuid.UUID('825d7aeb-05a9-45b5-a5b7-05df87923cda')), '825d7aeb-05a9-45b5-a5b7-05df87923cda')

    def test_hex_format(self):
        field = fields.UUID(dump_format='hex')
        self.assertEqual(field.dump(uuid.UUID('825d7aeb-05a9-45b5-a5b7-05df87923cda')), '825d7aeb05a945b5a5b705df87923cda')

    def test_int_format(self):
        field = fields.UUID(dump_format='int')
        self.assertEqual(field.dump(uuid.UUID('825d7aeb-05a9-45b5-a5b7-05df87923cda')), 173285016134224701509569922458251836634)

    def test_invalid_format(self):
        self.assertRaises(ValueError, fields.UUID, dump_format='invalid')

from contracts import fields, timezone
from contracts.exceptions import ValidationError
from datetime import datetime, date
from unittest import TestCase


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
        field = fields.Date()
        self.assertRaises(ValidationError, field.load, 'abc')

    def test_valid_inputs_with_min_max_value(self):
        field = fields.Float(min_value=1, max_value=3)
        self.assertEqual(field.load(1.0), 1.0)
        self.assertEqual(field.load(3.0), 3.0)

    def test_invalid_inputs_with_min_max_value(self):
        field = fields.Float(min_value=1, max_value=3)
        self.assertRaises(ValidationError, field.load, 0.9)
        self.assertRaises(ValidationError, field.load, 3.1)

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

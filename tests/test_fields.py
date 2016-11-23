import datetime

from contracts import fields, timezone
from contracts.exceptions import ValidationError
from unittest import TestCase


class FieldValues(object):
    """
    Base class for testing valid and invalid input values.
    """

    def get_items(self, mapping_or_list_of_two_tuples):
        # Tests accept either lists of two tuples, or dictionaries.
        if isinstance(mapping_or_list_of_two_tuples, dict):
            # {value: expected}
            return mapping_or_list_of_two_tuples.items()
        # [(value, expected), ...]
        return mapping_or_list_of_two_tuples

    def test_valid_inputs(self):
        """
        Ensure that valid values return the expected validated data.
        """
        for input_value, expected_output in self.get_items(self.valid_inputs):
            self.assertEqual(self.field.load(input_value), expected_output)

    def test_invalid_inputs(self):
        """
        Ensure that invalid values raise the expected validation error.
        """
        for input_value, expected_failure in self.get_items(self.invalid_inputs):
            with self.assertRaises(ValidationError) as exc_info:
                self.field.load(input_value)
            self.assertEqual(exc_info.exception.message, expected_failure)

    def test_outputs(self):
        for output_value, expected_output in self.get_items(self.outputs):
            self.assertEqual(self.field.dump(output_value), expected_output)


class TestBoolean(TestCase, FieldValues):
    """
    Valid and invalid values for `BooleanField`.
    """

    valid_inputs = {
        'True': True, 'true': True, 'TRUE': True,
        'False': False, 'false': False, 'FALSE': False,
        't': True, 'T': True,
        'f': False, 'F': False,
        '1': True, '0': False,
        1: True, 0: False,
        True: True, False: False,
    }
    invalid_inputs = {
        'foo': '"foo" is not a valid boolean.',
    }
    outputs = {
        'True': True, 'true': True, 'TRUE': True,
        'False': False, 'false': False, 'FALSE': False,
        't': True, 'T': True,
        'f': False, 'F': False,
        '1': True, '0': False,
        1: True, 0: False,
        True: True, False: False,
        'other': True,
    }
    field = fields.Boolean()


class TestDate(TestCase, FieldValues):
    """
    Valid and invalid values for `Date`.
    """
    valid_inputs = {
        '2001-01-20': datetime.date(2001, 1, 20),
        '20010120': datetime.date(2001, 1, 20),
        datetime.date(2001, 1, 20): datetime.date(2001, 1, 20),
        datetime.datetime(2001, 1, 20, 12, 00): datetime.date(2001, 1, 20)
    }
    invalid_inputs = {
        'abc': 'Date has wrong format.',
        '2001-99-99': 'Date has wrong format.',
    }
    outputs = {
        datetime.date(2001, 1, 20): '2001-01-20',
        datetime.datetime(2001, 1, 20, 12, 00): '2001-01-20',
    }
    field = fields.Date()


class TestDateTime(TestCase, FieldValues):
    """
    Valid and invalid values for `DateTimeField`.
    """
    valid_inputs = {
        '2001-01-01 13:00': datetime.datetime(2001, 1, 1, 13, 00, tzinfo=timezone.utc),
        '2001-01-01T13:00': datetime.datetime(2001, 1, 1, 13, 00, tzinfo=timezone.utc),
        '2001-01-01T13:00Z': datetime.datetime(2001, 1, 1, 13, 00, tzinfo=timezone.utc),
        datetime.datetime(2001, 1, 1, 13, 00): datetime.datetime(2001, 1, 1, 13, 00, tzinfo=timezone.utc),
        datetime.datetime(2001, 1, 1, 13, 00, tzinfo=timezone.utc): datetime.datetime(2001, 1, 1, 13, 00, tzinfo=timezone.utc),
    }
    invalid_inputs = {
        'abc': 'Datetime has wrong format.',
        '2001-99-99T99:00': 'Datetime has wrong format.',
        datetime.date(2001, 1, 1): 'Expected a datetime but got a date.',
    }
    outputs = {
        datetime.datetime(2001, 1, 1, 13, 00): '2001-01-01T13:00:00',
        datetime.datetime(2001, 1, 1, 13, 00, tzinfo=timezone.utc): '2001-01-01T13:00:00+00:00',
    }
    field = fields.DateTime(default_timezone=timezone.utc)

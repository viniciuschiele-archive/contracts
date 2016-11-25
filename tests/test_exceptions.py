from contracts.exceptions import ContractError, ValidationError
from unittest import TestCase


class TestValidationError(TestCase):
    def test_string_input(self):
        error = ValidationError('error')
        self.assertEqual(error.messages, ['error'])

    def test_dict_input(self):
        error = ValidationError({'code': 1234, 'message': 'error'})
        self.assertEqual(error.messages, [{'code': 1234, 'message': 'error'}])

    def test_list_input(self):
        error = ValidationError(['error'])
        self.assertEqual(error.messages, ['error'])


class TestContractError(TestCase):
    def test_error_with_field(self):
        error = ContractError()
        error.add_error(ValidationError('error', field_names=['property1']))
        self.assertEqual(error.messages, {'property1': ['error']})

    def test_error_with_fields(self):
        error = ContractError()
        error.add_error(ValidationError('error', field_names=['property1', 'property2']))
        self.assertEqual(error.messages, {'property1': ['error'], 'property2': ['error']})

    def test_error_without_field_name(self):
        error = ContractError()
        error.add_error(ValidationError('error'))
        self.assertEqual(error.messages, {'_contract': ['error']})

    def test_errors_with_same_field_name(self):
        error = ContractError()
        error.add_error(ValidationError('error 1', field_names=['property1']))
        error.add_error(ValidationError('error 2', field_names=['property1']))

        self.assertEqual(error.messages, {'property1': ['error 1', 'error 2']})

    def test_children_errors(self):
        child_error = ContractError()
        child_error.field_names = ['child']
        child_error.add_error(ValidationError('error', field_names=['property1']))

        parent_error = ContractError()
        parent_error.field_names = ['parent']
        parent_error.add_error(child_error)

        root_error = ContractError()
        root_error.add_error(parent_error)
        root_error.add_error(child_error)

        self.assertEqual(root_error.messages, {
            'parent': {
                'child': {
                    'property1': ['error']
                }
            },
            'child': {
                'property1': ['error']
            }})

    def test_children_errors_with_same_field_name(self):
        child_error = ContractError()
        child_error.field_names = ['child']
        child_error.add_error(ValidationError('error', field_names=['property1']))

        child_error2 = ContractError()
        child_error2.field_names = ['child']
        child_error2.add_error(ValidationError('error 2', field_names=['property2']))

        parent_error = ContractError()
        parent_error.add_error(child_error)
        parent_error.add_error(child_error2)

        self.assertEqual(parent_error.messages, {'child': {'property1': ['error'], 'property2': ['error 2']}})

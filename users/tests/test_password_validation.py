from django.test import SimpleTestCase
from django.core.exceptions import ValidationError
from users.password_validation import (
    NumberValidator, 
    LowerCaseValidator,
    UpperCaseValidator, 
    SymbolValidator
)


class TestPasswordValidators(SimpleTestCase):

    def test_number_password_validator__success(self):
        validator = NumberValidator()
        validator.validate('testuser123')

    def test_number_password_validator__failed(self):
        validator = NumberValidator()

        try:
            validator.validate('testuser')
            raise Exception('It should not validate!')
        except ValidationError:
            pass

    def test_lower_case_password_validator__success(self):
        validator = LowerCaseValidator()
        validator.validate('testUser123')

    def test_lower_case_password_validator__failed(self):
        validator = LowerCaseValidator()

        try:
            validator.validate('TESTUSER123')
            raise Exception('It should not validate!')
        except ValidationError:
            pass

    def test_upper_case_password_validator__success(self):
        validator = UpperCaseValidator()
        validator.validate('Testuser123')

    def test_upper_case_password_validator__failed(self):
        validator = UpperCaseValidator()

        try:
            validator.validate('testuser123')
            raise Exception('It should not validate!')
        except ValidationError:
            pass

    def test_symbol_password_validator__success(self):
        validator = SymbolValidator()
        allowed_symbols = ['#?!@$%^&*-/\()\'":;~`.,<>']
        for symbol in allowed_symbols:
            validator.validate(f'Testuser123{symbol}')

    def test_symbol_password_validator__failed(self):
        validator = SymbolValidator()

        try:
            validator.validate('testuser123')
            raise Exception('It should not validate!')
        except ValidationError:
            pass
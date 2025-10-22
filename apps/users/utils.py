import secrets

from django.core.exceptions import ValidationError


def check_otp_code(value):
    if len(str(value)) != 6:
        raise ValidationError("Otp code must be 6 digits")


def generate_code():
    numbers = '123456789'

    return "".join(secrets.choice(numbers) for i in range(6))
import re
from django.core.exceptions import ValidationError

def validate_password_strength(password: str):
    """
    Validate password strength:
    - Min 8 chars
    - At least 1 uppercase
    - At least 1 number
    - At least 1 special character
    """
    if len(password) < 8:
        raise ValidationError("Password must be at least 8 characters long.")
    if not re.search(r'[A-Z]', password):
        raise ValidationError("Password must contain at least one uppercase letter.")
    if not re.search(r'\d', password):
        raise ValidationError("Password must contain at least one number.")
    if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
        raise ValidationError("Password must contain at least one special character.")
    return password

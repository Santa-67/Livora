from marshmallow import ValidationError
import re


def validate_email(email):
    if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
        raise ValidationError('Invalid email address.')

def validate_phone(phone):
    if not re.match(r'^\+?\d{10,15}$', phone):
        raise ValidationError('Invalid phone number format (E.164).')

def validate_region(region):
    allowed_regions = [
        'Bangalore', 'Hyderabad', 'Pune', 'Chennai', 'Delhi NCR', 'Mumbai'
    ]
    if region not in allowed_regions:
        raise ValidationError(f'Region must be one of: {", ".join(allowed_regions)}')

def validate_budget(budget):
    if not (1000 <= budget <= 1000000):
        raise ValidationError('Budget must be between 1,000 and 1,000,000.')

def sanitize_text(text, max_length=5000):
    # Remove HTML tags and trim length
    text = re.sub(r'<.*?>', '', text)
    if len(text) > max_length:
        raise ValidationError(f'Text exceeds max length of {max_length} characters.')
    return text

def validate_password(password):
    if len(password) < 8:
        raise ValidationError('Password must be at least 8 characters.')
    if not re.search(r"[A-Z]", password):
        raise ValidationError('Password must contain an uppercase letter.')
    if not re.search(r"[a-z]", password):
        raise ValidationError('Password must contain a lowercase letter.')
    if not re.search(r"[0-9]", password):
        raise ValidationError('Password must contain a digit.')

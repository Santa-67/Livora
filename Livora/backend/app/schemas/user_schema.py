from app import ma
from app.models.user import User
from marshmallow import fields, validate

class UserSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = User
        load_instance = True
        include_fk = True
        exclude = ("password_hash",)
        unknown = 'exclude'
    password = fields.String(load_only=True, required=True)

    email = fields.Email(required=True, validate=[validate.Length(max=120)])
    name = fields.String(required=True, validate=[validate.Length(min=1, max=100)])
    phone = fields.String(validate=[validate.Regexp(r'^\+?\d{10,15}$', error="Invalid phone number format (E.164)."), validate.Length(max=20)])
    budget = fields.Integer(allow_none=True, validate=validate.Range(min=1000, max=1000000))
    lifestyle = fields.Dict()
    gender = fields.String(validate=validate.OneOf(["male", "female", "other"]))
    move_in_date = fields.Date(allow_none=True)
    bio = fields.String(allow_none=True, validate=validate.Length(max=500))
    avatar_url = fields.String(allow_none=True, validate=validate.Length(max=255))
    is_admin = fields.Boolean(dump_only=True)
    is_verified = fields.Boolean(dump_only=True)
    is_premium = fields.Boolean(dump_only=True)
    favorites = fields.List(fields.Raw())
    role = fields.String(dump_only=True)

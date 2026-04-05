from app import ma
from app.models.property import Property
from marshmallow import fields, validate

class PropertySchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Property
        load_instance = True
        include_fk = True
        # Set by server on create (POST body must not send these)
        exclude = ("id", "owner_id", "created_at", "updated_at")

    title = fields.String(required=True, validate=validate.Length(min=3, max=200))
    description = fields.String(required=True, validate=validate.Length(min=10, max=5000))
    rent = fields.Integer(required=True, validate=validate.Range(min=1000, max=1000000))
    location = fields.String(required=True, validate=validate.Length(max=200))
    latitude = fields.Float(allow_none=True)
    longitude = fields.Float(allow_none=True)
    images = fields.List(fields.String(validate=validate.Length(max=255)), allow_none=True)
    videos = fields.List(fields.String(validate=validate.Length(max=255)), allow_none=True)
    available = fields.Boolean()
    gender_preference = fields.String(
        allow_none=True, validate=validate.OneOf(["male", "female", "other"])
    )
    move_in_date = fields.Date(allow_none=True)
    amenities = fields.List(fields.String(validate=validate.Length(max=50)), allow_none=True)
    is_featured = fields.Boolean()
    is_verified = fields.Boolean()
    schedule_slots = fields.List(fields.Dict(), allow_none=True)
    housing_meta = fields.Dict(allow_none=True)

from app import db
from datetime import datetime

class Property(db.Model):
    __tablename__ = 'property'
    id = db.Column(db.Integer, primary_key=True)
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=False)
    rent = db.Column(db.Integer, nullable=False)
    location = db.Column(db.String(200), nullable=False)
    latitude = db.Column(db.Float)
    longitude = db.Column(db.Float)
    images = db.Column(db.JSON, default=list)  # list of image URLs
    videos = db.Column(db.JSON, default=list)  # list of video URLs
    available = db.Column(db.Boolean, default=True)
    gender_preference = db.Column(db.String(10))
    move_in_date = db.Column(db.Date)
    amenities = db.Column(db.JSON, default=list)  # e.g. ['wifi', 'ac', 'laundry']
    is_featured = db.Column(db.Boolean, default=False)
    is_verified = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    # Scheduling for virtual tours/visits
    schedule_slots = db.Column(db.JSON, default=list)  # [{date, time, booked_by}]
    # Optional Housing.csv–style fields for ML ranking: area, bedrooms, bathrooms, furnishing (0–2), region
    housing_meta = db.Column(db.JSON, default=dict)

    def to_dict(self):
        return {
            'id': self.id,
            'owner_id': self.owner_id,
            'title': self.title,
            'description': self.description,
            'rent': self.rent,
            'location': self.location,
            'latitude': self.latitude,
            'longitude': self.longitude,
            'images': self.images,
            'videos': self.videos,
            'available': self.available,
            'gender_preference': self.gender_preference,
            'move_in_date': self.move_in_date.isoformat() if self.move_in_date else None,
            'amenities': self.amenities,
            'is_featured': self.is_featured,
            'is_verified': self.is_verified,
            'created_at': self.created_at.isoformat(),
            'schedule_slots': self.schedule_slots,
            'housing_meta': self.housing_meta or {},
        }

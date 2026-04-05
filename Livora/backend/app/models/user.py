from app import db
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash

class User(db.Model):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(128))
    oauth_provider = db.Column(db.String(50))
    oauth_id = db.Column(db.String(128))
    name = db.Column(db.String(100), nullable=False)
    phone = db.Column(db.String(20), unique=True)
    budget = db.Column(db.Integer)
    lifestyle = db.Column(db.JSON)  # {sleep_time, cleanliness, pets, smoking, etc.}
    gender = db.Column(db.String(10))
    move_in_date = db.Column(db.Date)
    bio = db.Column(db.Text)
    avatar_url = db.Column(db.String(255))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    role = db.Column(db.String(20), default='tenant', nullable=False)  # tenant | owner | admin
    is_admin = db.Column(db.Boolean, default=False)
    is_verified = db.Column(db.Boolean, default=False)
    is_premium = db.Column(db.Boolean, default=False)
    last_login = db.Column(db.DateTime)
    # Relationships
    properties = db.relationship('Property', backref='owner', lazy=True)
    sent_messages = db.relationship('ChatMessage', foreign_keys='ChatMessage.sender_id', backref='sender', lazy=True)
    received_messages = db.relationship('ChatMessage', foreign_keys='ChatMessage.receiver_id', backref='receiver', lazy=True)
    matches = db.relationship('Match', foreign_keys='Match.user1_id', backref='user1', lazy=True)
    favorites = db.Column(db.JSON, default=list)  # List of property/user ids

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        if not self.password_hash:
            return False
        return check_password_hash(self.password_hash, password)

    def to_public_dict(self):
        """Safe fields for roommate discovery (no email)."""
        return {
            "id": self.id,
            "name": self.name,
            "bio": self.bio,
            "budget": self.budget,
            "lifestyle": self.lifestyle,
            "gender": self.gender,
            "move_in_date": self.move_in_date.isoformat() if self.move_in_date else None,
            "avatar_url": self.avatar_url,
            "is_verified": self.is_verified,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }

    def to_dict(self):
        return {
            'id': self.id,
            'email': self.email,
            'name': self.name,
            'phone': self.phone,
            'budget': self.budget,
            'lifestyle': self.lifestyle,
            'gender': self.gender,
            'move_in_date': self.move_in_date.isoformat() if self.move_in_date else None,
            'bio': self.bio,
            'avatar_url': self.avatar_url,
            'created_at': self.created_at.isoformat(),
            'is_admin': self.is_admin,
            'is_verified': self.is_verified,
            'is_premium': self.is_premium,
            'favorites': self.favorites,
            'role': self.role or 'tenant',
        }

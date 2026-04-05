from app import db
from datetime import datetime

class Match(db.Model):
    __tablename__ = 'match'
    id = db.Column(db.Integer, primary_key=True)
    user1_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    user2_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    compatibility_score = db.Column(db.Float, nullable=False)
    matched_on = db.Column(db.DateTime, default=datetime.utcnow)
    status = db.Column(db.String(20), default='pending')  # pending, accepted, rejected
    chat_id = db.Column(db.Integer, db.ForeignKey('chat_message.id'))
    initiator_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)

    def to_dict(self):
        return {
            'id': self.id,
            'user1_id': self.user1_id,
            'user2_id': self.user2_id,
            'compatibility_score': self.compatibility_score,
            'matched_on': self.matched_on.isoformat(),
            'status': self.status,
            'chat_id': self.chat_id,
            'initiator_id': self.initiator_id,
        }

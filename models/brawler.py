from flask_sqlalchemy import SQLAlchemy
from models import db


class Brawler(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    rarity = db.Column(db.String(30))
    health = db.Column(db.Integer)
    damage = db.Column(db.Integer)
    speed = db.Column(db.Integer)

    player_id = db.Column(db.Integer, db.ForeignKey('player.id', ondelete='SET NULL'))

    participations = db.relationship('BattleParticipant', backref='brawler', lazy=True, passive_deletes=True)

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "rarity": self.rarity,
            "health": self.health,
            "damage": self.damage,
            "speed": self.speed,
            "player_id": self.player_id
        }

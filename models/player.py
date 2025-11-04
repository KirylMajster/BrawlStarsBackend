from flask_sqlalchemy import SQLAlchemy
from models import db


class Player(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nickname = db.Column(db.String(50), unique=True, nullable=False)
    level = db.Column(db.Integer, default=1)
    total_trophies = db.Column(db.Integer, default=0)

    brawlers = db.relationship("Brawler", backref="player", lazy=True)
    participations = db.relationship('BattleParticipant', backref='player', lazy=True, passive_deletes=True)

    def to_dict(self):
        return {
            "id": self.id,
            "nickname": self.nickname,
            "level": self.level,
            "total_trophies": self.total_trophies,
            "brawlers": [b.name for b in self.brawlers]
        }

from datetime import date
from models import db

class Battle(db.Model):
    __tablename__ = 'battle'

    id = db.Column(db.Integer, primary_key=True)
    game_mode_id = db.Column(db.Integer, db.ForeignKey('gamemode.id', ondelete='SET NULL'))
    map_name = db.Column(db.String(100), nullable=False)
    date = db.Column(db.Date, default=date.today)
    result = db.Column(db.String(20))
    duration = db.Column(db.Integer)  # w sekundach

    def to_dict(self):
        return {
            "id": self.id,
            "game_mode_id": self.game_mode_id,
            "game_mode_name": self.game_mode.name if self.game_mode else None,
            "map_name": self.map_name,
            "date": self.date.isoformat(),
            "result": self.result,
            "duration": self.duration
        }
    
    participants = db.relationship(
    'BattleParticipant',
    backref='battle',
    lazy=True,
    passive_deletes=True  # honoruje ondelete=CASCADE
)


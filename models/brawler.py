from models import db


class Brawler(db.Model):
    __tablename__ = "brawler"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    rarity = db.Column(db.String(30))
    health = db.Column(db.Integer)
    damage = db.Column(db.Integer)
    speed = db.Column(db.Integer)

    trophies = db.Column(db.Integer, default=0)


    player_id = db.Column(
        db.Integer,
        db.ForeignKey("player.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,
    )

    player = db.relationship("Player", back_populates="brawler")

    participations = db.relationship(
        "BattleParticipant",
        backref="brawler",
        lazy=True,
        passive_deletes=True,
    )

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "rarity": self.rarity,
            "health": self.health,
            "damage": self.damage,
            "speed": self.speed,
            "trophies": self.trophies,
            "player_id": self.player_id,
        }

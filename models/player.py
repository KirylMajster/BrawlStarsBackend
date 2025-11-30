from models import db


class Player(db.Model):
    __tablename__ = "player"

    id = db.Column(db.Integer, primary_key=True)
    nickname = db.Column(db.String(50), unique=True, nullable=False)
    level = db.Column(db.Integer, default=1)
    total_trophies = db.Column(db.Integer, default=0)


    brawler = db.relationship(
        "Brawler",
        back_populates="player",
        uselist=False
    )


    participations = db.relationship(
        "BattleParticipant",
        backref="player",
        lazy=True,
        passive_deletes=True
    )

    def to_dict(self):
        return {
            "id": self.id,
            "nickname": self.nickname,
            "level": self.level,
            "total_trophies": self.total_trophies,
            "brawler_id": self.brawler.id if self.brawler else None,
            "brawler_name": self.brawler.name if self.brawler else None,
        }

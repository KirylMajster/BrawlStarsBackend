from models import db

class BattleParticipant(db.Model):
    __tablename__ = 'battle_participant'

    id = db.Column(db.Integer, primary_key=True)


    battle_id = db.Column(
        db.Integer,
        db.ForeignKey('battle.id', ondelete='CASCADE'),
        nullable=False
    )


    player_id = db.Column(
        db.Integer,
        db.ForeignKey('player.id', ondelete='SET NULL'),
        nullable=True
    )


    brawler_id = db.Column(
        db.Integer,
        db.ForeignKey('brawler.id', ondelete='SET NULL'),
        nullable=True
    )

    is_winner = db.Column(db.Boolean, default=False)


    __table_args__ = (
        db.UniqueConstraint('battle_id', 'player_id', name='uq_battle_player'),
    )

    def to_dict(self):
        return {
            "id": self.id,
            "battle_id": self.battle_id,
            "player_id": self.player_id,
            "brawler_id": self.brawler_id,
            "is_winner": self.is_winner
        }

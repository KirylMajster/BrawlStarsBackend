from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from config import Config
from sqlalchemy import event

# Import modeli
from models import db
from models.player import Player
from models.brawler import Brawler
from models.gamemode import GameMode
from models.battle import Battle
from models.battle_participant import BattleParticipant



# Import routes
from routes.player_routes import player_bp
from routes.brawler_routes import brawler_bp
from routes.gamemode_routes import gamemode_bp
from routes.battle_routes import battle_bp
from routes.battle_participant_routes import participant_bp



app = Flask(__name__)
app.config.from_object(Config)
db.init_app(app)

with app.app_context():
    @event.listens_for(db.engine, "connect")
    def enable_foreign_keys(dbapi_connection, connection_record):
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()

# Rejestracja blueprintów
app.register_blueprint(player_bp)
app.register_blueprint(brawler_bp)
app.register_blueprint(gamemode_bp)
app.register_blueprint(battle_bp)
app.register_blueprint(participant_bp)



@app.route("/")
def home():
    return "Witaj w moim API Brawl Stars!"

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)

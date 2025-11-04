from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import event

db = SQLAlchemy()


from models.player import Player
from models.brawler import Brawler

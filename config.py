import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))

class Config:
    # Ścieżka do bazy danych (SQLite)
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(BASE_DIR, 'brawlstars.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False

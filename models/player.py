from database import db
from datetime import datetime

class Player (db.Model):
    """ Player Model """

    __tablename__ = "players"

    id = db.Column(
        db.Integer,
        primary_key=True,
        autoincrement=True,
    )

    name = db.Column(
        db.String(50),
        nullable=False,
    )

    created_at = db.Column(
        db.DateTime,
        default=datetime.utcnow,
        nullable=False
    )

    last_active = db.Column(
        db.DateTime,
        default=datetime.utcnow,
        nullable=False
    )

    # direct navigation: player -> room & back (using 'players')
    lobbys = db.relationship(
        'Lobby',
        secondary='players_in_lobbys',
        backref='players'
    )

        


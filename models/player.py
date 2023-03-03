from database import db

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

    # direct navigation: player -> room & back (using 'players')
    rooms = db.relationship(
        'Room',
        secondary='players_in_rooms',
        backref='players'
    )


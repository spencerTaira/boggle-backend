from database import db

class Room (db.Model):
    """ Room Model"""

    __tablename__ = "rooms"

    room_name = db.Column(
        db.String(50),
        nullable=False,
        primary_key=True,
    )

    curr_players = db.Column(
        db.Integer,
        default=0,
        nullable=False,
    )

    max_players = db.Column(
        db.Integer,
        nullable=False,
    )

    # Time in seconds
    game_length = db.Column(
        db.Integer,
        nullable=False,
    )

    private = db.Column(
        db.Boolean,
        nullable=False,
    )

    password = db.Column(
        db.String(100),
        nullable=True,
    )

    host = db.Column(
        db.Integer,
        nullable=True,
    )

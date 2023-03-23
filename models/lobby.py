from database import db

class Lobby (db.Model):
    """ Lobby Model"""

    __tablename__ = "lobbys"

    lobby_name = db.Column(
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

    @property
    def serialize(self):
        return {
            "lobby_name": self.lobby_name,
            "curr_players": self.curr_players,
            "max_players": self.max_players,
            "game_length": self.game_length,
            "private": self.private,
            "password": self.password,
            "host": self.host,
        }

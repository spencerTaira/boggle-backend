from database import db

class PlayerInLobby (db.Model):
    """ Player in Lobby Model """

    __tablename__ = "players_in_lobbys"

    player_id = db.Column(
        db.Integer,
        db.ForeignKey('players.id'),
        nullable=False,
        primary_key=True,
    )

    lobby_id = db.Column(
        db.String,
        db.ForeignKey('lobbys.lobby_name'),
        nullable=False,
    )
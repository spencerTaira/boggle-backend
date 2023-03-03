from database import db

class PlayerInRoom (db.Model):
    """ Player in Room Model """

    __tablename__ = "players_in_rooms"

    player_id = db.Column(
        db.Integer,
        db.ForeignKey('players.id'),
        nullable=False,
        primary_key=True,
    )

    room_id = db.Column(
        db.String,
        db.ForeignKey('rooms.room_name'),
        nullable=False,
        primary_key=True,
    )
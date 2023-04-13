from database import db

class PlayerClientId (db.Model):
    """Pairing of player to client websocket ID model"""
    
    __tablename__ = "player_and_client"
    
    client_id = db.Column(
        db.String,
        nullable=False,
        primary_key=True,
    )
    
    player_id = db.Column(
        db.Integer,
        db.ForeignKey('players.id'),
        nullable=False,
    )
    
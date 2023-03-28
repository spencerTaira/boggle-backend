from flask import Blueprint, jsonify, request, session
from database import db
from models.lobby import Lobby
from models.player import Player
from models.player_in_lobby import PlayerInLobby
from app import bcrypt
player = Blueprint("player", __name__)

@player.get("/")
def get_player():
    """
    Gets a players data
        Input: 
            {
                playerId: 1
            }
            
        Output:
            {
                playerId:1
                playeName: test
                currentConnectionId: 12345
            }
    """
    
    player = request.args["playerId"]
    
    
from flask import Blueprint, jsonify, request, session
from database import db
from models.lobby import Lobby
from models.player import Player
from models.player_in_lobby import PlayerInLobby
from app import bcrypt
# from sqlalchemy import exc

player = Blueprint("player", __name__)

@player.get("")
def get_player():
    """
    Gets a players data
        Input:
            {
                playerId: 1
            }

        Output:
            {
                playerId:1,
                playerName: test
            }
    """
    print("\033[96m"+"\n\n\Get player route entered\n\n\n" + "\033[00m")

    player_id = request.args["playerId"]
    player = Player.query.get(player_id)

    if player:
        player_data = {
            "playerId": player.id,
            "playerName": player.name
        }
        return (jsonify(playerData=player_data), 200)
    else:
        return (jsonify(error=f"Player {player_id} not found."), 404)

@player.post("")
def create_player():
    """
    Create a player in the database
        Input:
            {
                playerName: 'player 1'
            }

        Output:
            {
                playerId: 1,
                playerName: 'player 1'
            }
    """
    print("\033[96m"+"\n\n\nEntered create_player route\n\n\n" + "\033[00m")
    player_name = request.json['playerName']
    player = Player(
        name=player_name
    )

    try:
        db.session.add(player)
        db.session.commit()
    # except exc.SQLAlchemyError as e:
    except Exception as e:
        print('Error reason', e.args[0])
        if 'value too long' in e.args[0]:
            db.session.rollback()
            return (jsonify(error="Name is too long. Please do not exceed 50 chars"), 400)
        return (jsonify(error="Unknown Error Maybe Server???"), 500)

    player_data = {
        "playerId": player.id,
        "playerName": player.name
    }
    print("\033[96m"+"\n\n\nEnd create_player route\n\n\n" + "\033[00m")
    return (jsonify(playerData=player_data), 201)
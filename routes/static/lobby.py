from flask import Blueprint, jsonify, request, session
from database import db
from models.lobby import Lobby
from models.player import Player
from models.player_in_lobby import PlayerInLobby
from app import bcrypt
lobby = Blueprint("lobby", __name__)

@lobby.get("/")
def get_lobby():
    """
    Gets a game lobby.  If it does not exist, return error.

        Input: JSON Like:
        {
            lobbyName: 'test lobby'
        }

        Output:
        {
	        "lobbyData": {
		        "curr_players": 0,
		        "game_length": 60,
		        "host": null,
		        "lobby_name": "test lobby",
		        "max_players": 2,
		        "private": true
	        }
        }

        or

        {
	        "error": "Lobby test lobby does not exist!!!!!!"
        }

    """

    print('Get lobby route entered')

    lobby_name = request.args["lobbyName"]

    lobby = Lobby.query.get(lobby_name)
    if not lobby:
        return (jsonify(error=f"Lobby {lobby_name} does not exist!!!!!!"), 404)

    lobby_data = lobby.serialize
    del lobby_data["password"]

    return (jsonify(lobbyData=lobby_data), 200)

@lobby.post("/create")
def create_lobby():
    """
    Create a game lobby
        Input: JSON Like:
        {
            lobbyName: 'test lobby',
            password: 'password',
            maxPlayers: 2,
            gameLength: 60 (in secs),
        }

        Output:
        {
            lobbyName: 'test lobby',
            password: 'password'
            maxPlayers: 2,
            gameLength: 60 (in secs),
        }
    """

    print("Create lobby route entered")
    lobby_name = request.json["lobbyName"]
    password = request.json["password"]
    max_players = request.json["maxPlayers"]
    game_length = request.json["gameLength"]

    existing = Lobby.query.get(lobby_name)
    if existing:
        return ("Error, lobby exists", 403)

    pw_hash = bcrypt.generate_password_hash(password).decode("utf-8")
    print("what is pw_hash>>>>>>>>>>>>>>>", pw_hash)
    lobby = Lobby(
        lobby_name=lobby_name,
        password=pw_hash,
        max_players=max_players,
        game_length=game_length,
        private=True, #this is default may want to allow for non-private games later
    )
    lobby_info = {
        'lobbyName':lobby_name,
        'maxPlayers':max_players,
        'gameLength':game_length,
    }
    try:

        db.session.add(lobby)
        db.session.commit()
        #update open lobbys visible to other connected clients
        return (jsonify(lobbyInfo = lobby_info), 200)

    except Exception as e:
        db.session.rollback()
        return ("Error creating lobby", 403)

@lobby.get("/validate")
def validate_lobby_credentials():
    """
        Enter a lobby

        Input: JSON Like:
        {
            lobbyName: 'test lobby',
            password: 'password',
        }

        Output: JSON Like:
        {
            lobbyName: 'test lobby'
            authenticated: True
        }
    """
    print("/enter route entered")

    lobby_name = request.args["lobbyName"]
    password = request.args["password"]

    lobby = Lobby.query.get(lobby_name)
    if not lobby:
        return(jsonify(error="Lobby/password incorrect"), 403)

    if bcrypt.check_password_hash(lobby.password, password):
        authentication = {
            "lobbyName":lobby.lobby_name,
            "authenticated": True
        }

        return (jsonify(authentication=authentication), 200)
    else:
        return(jsonify(error="Lobby/password incorrect"), 403)

@lobby.post("/join")
def join_lobby():
    """
        Join a lobby

        Input: JSON like:
        {
            playerName: 'testPlayer',
            lobbyId: 'lobby100'
        }

        Output: JSON like:
        {
            playerId: 1,
            playerName: 'testPlayer',
            currLobbyId: 'lobby100',
        }

    """
    print("/join route entered")

    player_name = request.json['playerName']
    lobby_name = request.json['lobbyId']

    player = Player(
        name = player_name,
    )

    lobby = Lobby.query.get(lobby_name)

    if not lobby:
        return(jsonify(error="Lobby does not exist"), 400)

    if lobby.curr_players == lobby.max_players:
        return(jsonify(error="Lobby is full"), 400)

    try:
        lobby.players.append(player)
        lobby.curr_players += 1
        db.session.commit()
    except:
        db.session.rollback()
        return ("Error creating player")

    if not lobby.host:
        print('Lobby HOST ----------------------------------------', lobby.host)
        lobby.host = player.id
        db.session.commit()

    # updated_lobby = Lobby.query.get(lobby_name)

    player_data = {
        'playerId': player.id,
        'playerName':player.name,
        'currLobbyId': lobby.lobby_name
    }

    return (jsonify(playerData=player_data), 201)







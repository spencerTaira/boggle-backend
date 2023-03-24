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
    Gets a game lobby
        Input: JSON Like:
        {
            lobbyName: 'test lobby'
        }

        Output:
        {
            lobbyName: 'test lobby',
        }
    """

    print('Get lobby route entered')

    lobby_name = request.args["lobbyName"]

    lobby = Lobby.query.get(lobby_name)
    if not lobby:
        return (jsonify(error=f"Lobby {lobby_name} does not exist!!!!!!"), 404)
    if (lobby.curr_players >= lobby.max_players):
        return (f"Lobby {lobby_name} is full!!!", 400)

    return (lobby.lobby_name, 200)

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

@lobby.get("/enter")
def enter_lobby():
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
        }
    """
    print("/enter route entered")

    lobby_name = request.args["lobbyName"]
    password = request.args["password"]

    lobby = Lobby.query.get(lobby_name)
    if not lobby:
        return("Lobby/password incorrect", 403)

    if bcrypt.check_password_hash(lobby.password, password):

        return (jsonify(lobbyName=lobby_name), 200)
    else:
        return ("Lobby/password incorrect", 403)

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
            host: False
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
        return ("Lobby does not exist", 400)

    if lobby.curr_players == lobby.max_players:
        return ("Lobby is full", 400)

    #TODO: set creator or host if first person to join lobby

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
        'host': lobby.host == player.id,
    }

    return (jsonify(playerData=player_data), 201)








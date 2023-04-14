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
		        "game_length": 60,
		        "host": 1,
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
    print("\033[96m"+"\n\n\Get lobby route entered\n\n\n" + "\033[00m")

    lobby_name = request.args["lobbyName"]

    lobby = Lobby.query.get(lobby_name)
    if not lobby:
        return (jsonify(error=f"Lobby {lobby_name} does not exist!!!!!!"), 404)

    lobby_data = lobby.serialize
    # del lobby_data["password"]

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
            playerId: 1
        }

        Output:
        {
            lobbyName: 'test lobby',
        }
    """

    print("\033[96m"+"\n\n\Create lobby route entered\n\n\n" + "\033[00m")
    lobby_name = request.json["lobbyName"]
    password = request.json["password"]
    max_players = request.json["maxPlayers"]
    game_length = request.json["gameLength"]
    player_id = request.json["playerId"]

    existing = Lobby.query.get(lobby_name)
    if existing:
        return (jsonify(error="Error, lobby exists"), 403)

    pw_hash = bcrypt.generate_password_hash(password).decode("utf-8")

    lobby = Lobby(
        lobby_name=lobby_name,
        password=pw_hash,
        max_players=max_players,
        game_length=game_length,
        host=player_id,
        private=True, #this is default may want to allow for non-private games later
    )

    player = Player.query.get(player_id)

    try:

        db.session.add(lobby)
        player_in_lobby = PlayerInLobby.query.get(player_id)
        if(player_in_lobby == None):
            lobby.players.append(player)
        else:
            player_in_lobby.lobby_id = lobby_name
        db.session.commit()
        #update open lobbys visible to other connected clients

    except Exception as e:
        db.session.rollback()
        return (jsonify(error="Error creating lobby"), 403)


    return (jsonify(lobbyName = lobby.lobby_name), 201)

@lobby.post("/join")
def validate_lobby_credentials_and_join():
    """
        Enter a lobby

        Input: JSON Like:
        {
            lobbyName: 'test lobby',
            password: 'password',
            playerId: 1
        }

        Output: JSON Like:
        {
            lobbyName: 'test lobby'
        }
    """
    print("\033[96m"+"\n\n\nJoin lobby route entered\n\n\n" + "\033[00m")

    lobby_name = request.json["lobbyName"]
    password = request.json["password"]
    player_id = request.json["playerId"]

    lobby = Lobby.query.get(lobby_name)
    player = Player.query.get(player_id)


    if not lobby:
        return(jsonify(error="Lobby/password incorrect"), 403)

    if not player:
        return(jsonify(error="Player doesn't exist"), 403)

    if bcrypt.check_password_hash(lobby.password, password):
        num_players_in_lobby = len(PlayerInLobby.query.filter_by(lobby_id=lobby_name).all())
        # print("\033[96m"+f"\n\n\nNumber of players in lobby, {num_players_in_lobby}\n\n\n" + "\033[00m")

        if num_players_in_lobby >= lobby.max_players:
            return (jsonify(error="Lobby is full"), 400)

        try:
            player_in_lobby = PlayerInLobby.query.get(player_id)
            if (player_in_lobby):
                player_in_lobby.lobby_id = lobby_name
            else:
                lobby.players.append(player)
            db.session.commit()
        except :
            return (jsonify(error="It's our fault. Could not join lobby"), 500)

        lobby_name = lobby.lobby_name

        return (jsonify(lobbyName=lobby_name), 200)
    else:
        return(jsonify(error="Lobby/password incorrect"), 403)

@lobby.post("/rejoin")
def rejoin_lobby():
    print("\033[96m"+"\n\n\nRejoin lobby route entered\n\n\n" + "\033[00m")
    current_lobby = request.json['currLobby']
    player_id = request.json['playerId']

    lobby = Lobby.query.get(current_lobby)
    player = Player.query.get(player_id)

    if not lobby:
        return(jsonify(error="Lobby doesn't exist"), 403)

    if not player:
        return(jsonify(error="Player doesn't exist"), 403)

    num_players_in_lobby = len(PlayerInLobby.query.filter_by(lobby_id=current_lobby).all())

    if num_players_in_lobby >= lobby.max_players:
        return (jsonify(error="Lobby is full"), 400)

    try:
        player_in_lobby = PlayerInLobby.query.get(player_id)
        if (player_in_lobby):
            player_in_lobby.lobby_id = current_lobby
        else:
            lobby.players.append(player)
        db.session.commit()
    except :
        return (jsonify(error="It's our fault. Could not join lobby"), 500)

    lobby_name = lobby.lobby_name

    return (jsonify(lobbyName=lobby_name), 200)


# @lobby.post("/join")
# def join_lobby():
#     """
#         Join a lobby

#         Input: JSON like:
#         {
#             playerName: 'testPlayer',
#             lobbyId: 'lobby100'
#         }

#         Output: JSON like:
#         {
#             playerId: 1,
#             playerName: 'testPlayer',
#             currLobbyId: 'lobby100',
#         }

#     """
#     print("/join route entered")

#     player_name = request.json['playerName']
#     lobby_name = request.json['lobbyId']

#     player = Player(
#         name = player_name,
#     )

#     lobby = Lobby.query.get(lobby_name)

#     if not lobby:
#         return(jsonify(error="Lobby does not exist"), 400)

#     if lobby.curr_players == lobby.max_players:
#         return(jsonify(error="Lobby is full"), 400)

#     try:
#         lobby.players.append(player)
#         lobby.curr_players += 1
#         db.session.commit()
#     except:
#         db.session.rollback()
#         return ("Error creating player")

#     if not lobby.host:
#         print('Lobby HOST ----------------------------------------', lobby.host)
#         lobby.host = player.id
#         db.session.commit()

#     # updated_lobby = Lobby.query.get(lobby_name)

#     player_data = {
#         'playerId': player.id,
#         'playerName':player.name,
#         'currLobbyId': lobby.lobby_name
#     }

#     return (jsonify(playerData=player_data), 201)








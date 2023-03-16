from flask import Blueprint, jsonify, request, session
from database import db
from models.room import Room
from models.player import Player
from models.player_in_room import PlayerInRoom
from app import bcrypt
room = Blueprint("room", __name__)

@room.post("/create")
def create_room():
    """
    Create a game room
        Input: JSON Like:
        {
            roomName: 'test room',
            password: 'password',
            maxPlayers: 2,
            gameLength: 60 (in secs),
        }

        Output:
        {
            roomName: 'test room',
            maxPlayers: 2,
            gameLength: 60 (in secs),
        }
    """

    print("Create room route entered")
    room_name = request.json["roomName"]
    password = request.json["password"]
    max_players = request.json["maxPlayers"]
    game_length = request.json["gameLength"]

    existing = Room.query.get(room_name)
    if existing:
        return ("Error, room exists", 403)

    pw_hash = bcrypt.generate_password_hash(password).decode("utf-8")
    print("what is pw_hash>>>>>>>>>>>>>>>", pw_hash)
    room = Room(
        room_name=room_name,
        password=pw_hash,
        max_players=max_players,
        game_length=game_length,
        private=True, #this is default may want to allow for non-private games later
    )
    room_info = {
        'roomName':room_name,
        'maxPlayers':max_players,
        'gameLength':game_length,
    }
    try:

        db.session.add(room)
        db.session.commit()
        #update open rooms visible to other connected clients
        return (jsonify(roomInfo = room_info), 200)

    except Exception as e:
        db.session.rollback()
        return ("Error creating room", 403)

@room.get("/enter")
def enter_room():
    """
        Enter a room

        Input: JSON Like:
        {
            roomName: 'test room',
            password: 'password',
        }

        Output: JSON Like:
        {
            roomName: 'test room'
        }
    """
    print("/enter route entered")

    room_name = request.args["roomName"]
    password = request.args["password"]

    room = Room.query.get(room_name)
    if not room:
        return("Room/password incorrect", 403)

    if bcrypt.check_password_hash(room.password, password):

        return (jsonify(roomName=room_name), 200)
    else:
        return ("Room/password incorrect", 403)

@room.post("/join")
def join_room():
    """
        Join a room

        Input: JSON like:
        {
            playerName: 'testPlayer',
            roomId: 'room100'
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
    room_name = request.json['roomId']

    player = Player(
        name = player_name,
    )

    room = Room.query.get(room_name)

    if not room:
        return ("Room does not exist")

    if room.curr_players == room.max_players:
        return ("Room is full")

    #TODO: set creator or host if first person to join room

    try:
        room.players.append(player)
        room.curr_players += 1
        db.session.commit()
    except:
        db.session.rollback()
        return ("Error creating player")

    if not room.host:
        print('ROOM HOST ----------------------------------------', room.host)
        room.host = player.id
        db.session.commit()

    # updated_room = Room.query.get(room_name)

    player_data = {
        'playerId': player.id,
        'playerName':player.name,
        'host': room.host == player.id,
    }

    return (jsonify(playerData=player_data), 201)








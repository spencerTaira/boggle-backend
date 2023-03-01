from flask import Blueprint, jsonify, request
from database import db
from models.room import Room

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
    """

    print("<!_!_!_!_!_!_!_!_!_!_!_!__________!!!!!!!!!!!!>", request.json);
    room_name = request.json["roomName"]
    password = request.json["password"]
    max_players = request.json["maxPlayers"]
    game_length = request.json["gameLength"]

    room = Room(
        room_name=room_name,
        password=password,
        max_players=max_players,
        game_length=game_length,
        private=True, #this is default may want to allow for non-private games later
    )

    #Will we need a try/catch?
    db.session.add(room)
    db.session.commit()

    return ("great success", 200)
from flask import Blueprint, jsonify, request
from database import db
from models.room import Room
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
    """

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
    
    try:
    
        db.session.add(room)
        db.session.commit()
        #update open rooms visible to other connected clients
        return (jsonify(roomName=room_name), 200)

    except Exception as e:
        db.session.rollback()
        return ("Error creating room", 403)
    
@room.get("/enter")
def enter_room():
    """
        Join a room
        
        Input: JSON Like:
        {
            roomName: 'test room',
            password: 'password',
        }
    """
    
    room_name = request.json["roomName"]
    password = request.json["password"]
    
    room = Room.query.get(room_name)
    if not room:
        return("Room/password incorrect", 403)
    
    if bcrypt.check_password_hash(room.password, password):
        return (jsonify(roomName=room_name), 200)
    else:
        return ("Room/password incorrect", 403)
    

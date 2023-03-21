from flask_cors import CORS
from flask import Flask, request, render_template, jsonify
from flask_socketio import SocketIO, emit
from database import connect_db
from config import DATABASE_URL
from uuid import uuid4
from flask_bcrypt import Bcrypt
from boggle import BoggleGame
from models.room import Room
import json

app = Flask(__name__)
app.config["SECRET_KEY"] = "this-is-secret"
app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE_URL
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SQLALCHEMY_ECHO"] = True

bcrypt = Bcrypt(app)
socketio = SocketIO(app, logger=True, engineio_logger=True, cors_allowed_origins="*")


from routes.static.room import room

# register blueprints
app.register_blueprint(room, url_prefix="/room")


@socketio.on('connect')
def connect():
    """
        Initialize websocket connection
    """

    emit('connected', 'Hello')

@socketio.on('intro-get-rooms')
def show_rooms():
    """
        Get active public rooms and send to front-end
    """

    rooms = Room.query.filter(Room.curr_players < Room.max_players).all()
    rooms_serialized = [room.serialize for room in rooms]
    # print('<!!!!!-------------------------------------!!!!!!>', rooms_json)
    emit('intro-send-rooms', rooms_serialized)

if __name__ == '__main__':
    socketio.run(app)
CORS(app)
connect_db(app)



# The boggle games created, keyed by game id
# games = {}

# @app.get("/")
# def homepage():
#     """Show board."""

#     return render_template("index.html")


# @app.post("/api/new-game")
# def new_game():
#     """Start a new game and return JSON: {game_id, board}."""

#     # get a unique string id for the board we're creating
#     game_id = str(uuid4())
#     game = BoggleGame()
#     games[game_id] = game

#     return {"gameId": "need-real-id", "board": "need-real-board"}
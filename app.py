from flask_cors import CORS
from flask import Flask, request, render_template, jsonify
from flask_socketio import SocketIO, emit
from database import connect_db
from config import DATABASE_URL
from uuid import uuid4
from flask_bcrypt import Bcrypt
from boggle import BoggleGame
from models.lobby import Lobby
# from models.player import player
import json

app = Flask(__name__)
app.config["SECRET_KEY"] = "this-is-secret"
app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE_URL
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SQLALCHEMY_ECHO"] = True

bcrypt = Bcrypt(app)
socketio = SocketIO(app, logger=True, engineio_logger=True, cors_allowed_origins="*")


from routes.static.lobby import lobby
from routes.static.player import player

# register blueprints
app.register_blueprint(lobby, url_prefix="/lobby")
app.register_blueprint(player, url_prefix="/player")


@socketio.on('connect')
def connect():
    """
        Initialize websocket connection
    """

    emit('connected', 'Hello')

@socketio.on('intro-get-lobbys')
def show_lobbys():
    """
        Get active public lobbys and send to front-end
    """

    lobbys = Lobby.query.filter(Lobby.curr_players < Lobby.max_players).all()
    lobbys_serialized = [lobby.serialize for lobby in lobbys]
    # print('<!!!!!-------------------------------------!!!!!!>', lobbys_json)
    emit('intro-send-lobbys', lobbys_serialized)

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
from flask_cors import CORS
from flask import Flask, request, render_template, jsonify
from flask_caching import Cache
from flask_socketio import SocketIO, emit, join_room, leave_room
from database import connect_db, db
from config import DATABASE_URL, SECRET_KEY
from uuid import uuid4
from flask_bcrypt import Bcrypt
from boggle import BoggleGame
from models.lobby import Lobby
from models.player_in_lobby import PlayerInLobby
from routes.websockets.intro import IntroNamespace
from routes.websockets.lobby import LobbyNamespace
# from models.player import player

app = Flask(__name__)
app.config["SECRET_KEY"] = SECRET_KEY
app.config['SQLALCHEMY_DATABASE_URI'] = (
    DATABASE_URL.replace("postgres://", "postgresql://"))
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SQLALCHEMY_ECHO"] = True

# Cache config
config = {
    "DEBUG": True,          # some Flask specific configs
    "CACHE_TYPE": "SimpleCache",  # Flask-Caching related configs
    "CACHE_DEFAULT_TIMEOUT": 300
}

app.config.from_mapping(config)
cache = Cache(app)

bcrypt = Bcrypt(app)
socketio = SocketIO(
    app, logger=True,
    engineio_logger=True,
    cors_allowed_origins="*",
    async_mode='eventlet',
    reconnection=True
)

# socketio.connection_state_recovery = {
#     # the backup duration of the sessions and the packets
#     'max_disconnection_duration': 2 * 60 * 1000,
#     # whether to skip middlewares upon successful recovery
#     'skip_middlewares': True,
# }

from routes.static.lobby import lobby
from routes.static.player import player

# register blueprints
app.register_blueprint(lobby, url_prefix="/lobby")
app.register_blueprint(player, url_prefix="/player")

# register websocket namespaces
socketio.on_namespace(IntroNamespace('/intro'))
socketio.on_namespace(LobbyNamespace('/lobby'))

@app.get("/ping-pong")
def ping_pong():
    """
    Workaround for Render 15 minute Idle. Websockets don't count.
    """

    print("\033[96m"+"\n\n\nGot Pingged Yo\n\n\n" + "\033[00m")

    pong = "pong"
    return (jsonify(pong=pong), 200)

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
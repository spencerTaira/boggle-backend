from flask_cors import CORS
from flask import Flask, request, render_template, jsonify
from flask_socketio import SocketIO, emit, join_room, leave_room
from database import connect_db, db
from config import DATABASE_URL
from uuid import uuid4
from flask_bcrypt import Bcrypt
from boggle import BoggleGame
from models.lobby import Lobby
from models.player_in_lobby import PlayerInLobby
# from models.player import player


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


# @socketio.on('connect')
# def connect():
#     """
#         Initialize websocket connection
#     """
#     print("\033[95m"+"\nWEBSOCKET: Connected\n" + "\033[00m")
#     emit('connected', 'Success')

@socketio.on('intro-get-lobbys')
def show_lobbys():
    """
        Get active public lobbys and send to front-end
    """

    print("\033[95m"+"\nWEBSOCKET: Intro-get-lobbys\n" + "\033[00m")

    """
        num_players_in_lobbys (list of tuples)

        create an empty list
        iterate through num_players_in_lobbys
        query.get(lobby_id)
        check if (num_players) is less than lobby.max_players
            if it is push into list


        SELECT lobbys.lobby_name, lobbys.max_players, pil.curr_players
            FROM lobbys
            LEFT JOIN (
                SELECT lobby_id, COUNT(lobby_id) AS curr_players
                    FROM players_in_lobbys
                    GROUP BY lobby_id
            ) as pil
            ON lobbys.lobby_name = pil.lobby_id
                WHERE pil.curr_players < lobbys.max_players
                    OR pil.curr_players is NULL;

    """

    print("\033[95m"+"\nPre Sub Query\n" + "\033[00m")
    subquery = db.session.query(
        PlayerInLobby.lobby_id, db.func.count(PlayerInLobby.lobby_id)
            .label('curr_players')
        ).group_by(PlayerInLobby.lobby_id
    ).subquery()

    print("\033[95m"+"\nPost Sub Query\n" + "\033[00m")
    query = db.session.query(
        Lobby.lobby_name, Lobby.max_players, subquery.c.curr_players
    ).outerjoin(
        subquery, Lobby.lobby_name == subquery.c.lobby_id
    ).filter(
        (subquery.c.curr_players < Lobby.max_players) | (subquery.c.curr_players == None)
    )

    non_full_lobbys = query.all()

    lobbys_serialized = []
    for row in non_full_lobbys:
        lobby = {
            "lobby_name":row.lobby_name,
            "max_players":row.max_players,
            "curr_players":row.curr_players
        }
        lobbys_serialized.append(lobby)

    emit('intro-send-lobbys', lobbys_serialized)

@socketio.on('joining')
def player_joined(player_data):
    player_name = player_data['playerName']
    current_lobby = player_data['currLobby']
    join_room(current_lobby)
    emit('joined', {"playerName":player_name, "message":f"{player_name} has joined the lobby"})

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
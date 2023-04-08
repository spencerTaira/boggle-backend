from flask_cors import CORS
from flask import Flask, request, render_template, jsonify
from flask_socketio import SocketIO, emit
from database import connect_db, db
from config import DATABASE_URL
from uuid import uuid4
from flask_bcrypt import Bcrypt
from boggle import BoggleGame
from models.lobby import Lobby
from models.player_in_lobby import PlayerInLobby
# from models.player import player
import json
from sqlalchemy import func, select, literal_column, label, join

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

    print("\033[95m"+"\nWEBSOCKET: Intro-get-lobbys\n" + "\033[00m")

    # num_players_in_lobbys = PlayerInLobby.query.with_entities(
    #     PlayerInLobby.lobby_id,
    #     func.count()
    # ).group_by(PlayerInLobby.lobby_id).all()

    # print("\033[95m"+f"\n\n\nNum_players_in_lobbys {num_players_in_lobbys}\n\n\n" + "\033[00m")

    lobbys = Lobby.query.all()

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



    #TODO: Add this to our route
        subq = (
    select([
        PlayersInLobby.lobby_id,
        func.count(PlayersInLobby.lobby_id).label('curr_players')
    ])
    .group_by(PlayersInLobby.lobby_id)
    .subquery('pil')
)

query = (
    select([
        Lobby.lobby_name,
        Lobby.max_players,
        subq.c.curr_players
    ])
    .select_from(Lobby.outerjoin(subq, Lobby.lobby_name == subq.c.lobby_id))
    .where((subq.c.curr_players < Lobby.max_players) | (subq.c.curr_players == None))
)

result = db.session.execute(query)
for row in result:
    print(row.lobby_name, row.max_players, row.curr_players)


    """

    # subq = select(
    #     func.count(PlayerInLobby.lobby_id)
    # ).where(PlayerInLobby.lobby_id == Lobby.lobby_name).scalar_subquery()

    # non_empty_lobbys = Lobby.query.filter(Lobby.max_players > subq).all()

    #     # non_full_lobbys = [lobby for lobby in lobbys if lobby.max_players <= ]
    # lobbys_serialized = [lobby.serialize for lobby in non_empty_lobbys]
    # print("\033[95m"+f"\n\n\nNum_players_in_lobbys {lobbys_serialized}\n\n\n" + "\033[00m")

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

    
    # subq = (
    #     select(
    #         PlayerInLobby.lobby_id,
    #         func.count(PlayerInLobby.lobby_id).label('curr_players')
    #     )
    #     .group_by(PlayerInLobby.lobby_id)
    #     .subquery('pil')
    # )


    # j = join(Lobby, subq, Lobby.lobby_name == subq.c.lobby_id)

    # query = (
    #     select(
    #         Lobby.lobby_name,
    #         Lobby.max_players,
    #         subq.c.curr_players
    #     )
    #     .select_from(j)
    #     .where((subq.c.curr_players < Lobby.max_players) | (subq.c.curr_players == None))
    # )

    # query = (
    #     select(
    #         Lobby.lobby_name,
    #         Lobby.max_players,
    #         subq.c.curr_players
    #     )
    #     .select_from(Lobby.outerjoin(subq, Lobby.lobby_name == subq.c.lobby_id))
    #     .where((subq.c.curr_players < Lobby.max_players) | (subq.c.curr_players == None))
    # )

    print("\033[95m"+"\nPre Query\n" + "\033[00m")
    # non_full_lobbys = db.session.execute(query)
    non_full_lobbys = query.all()
    print("\033[95m"+"\nExecuted Query\n" + "\033[00m")

    print("\033[95m")
    #FIXME: Not seeing empty lobby (not sure if SQL filter is working properly)
    #FIXME: Can't get length of non_full_lobbys, is that normal? try pdb
    print('Number of non full lobbys', len(non_full_lobbys))
    for row in non_full_lobbys:
        print('each time')
        print(row.lobby_name, row.max_players, row.curr_players)
    print("\033[00m")
    lobbys_serialized = []
    for row in non_full_lobbys:
        lobby = {"lobby_name":row.lobby_name, "max_players":row.max_players, "curr_players":row.curr_players}
        lobbys_serialized.append(lobby)
    
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
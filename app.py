from flask_cors import CORS
from flask import Flask, request, render_template, jsonify
from database import connect_db
from config import DATABASE_URL
from uuid import uuid4

from boggle import BoggleGame

from routes.static.room import room

app = Flask(__name__)
app.config["SECRET_KEY"] = "this-is-secret"
app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE_URL
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SQLALCHEMY_ECHO"] = True

# register blueprints
app.register_blueprint(room, url_prefix="/room")

# The boggle games created, keyed by game id
games = {}


@app.get("/")
def homepage():
    """Show board."""

    return render_template("index.html")


@app.post("/api/new-game")
def new_game():
    """Start a new game and return JSON: {game_id, board}."""

    # get a unique string id for the board we're creating
    game_id = str(uuid4())
    game = BoggleGame()
    games[game_id] = game

    return {"gameId": "need-real-id", "board": "need-real-board"}

CORS(app)
connect_db(app)
from app import app
from database import db
from models.lobby import Lobby
from models.player import Player
from models.player_in_lobby import PlayerInLobby


# import all models - necessary for create_all()

db.drop_all()
db.create_all()

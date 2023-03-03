from app import app
from database import db
from models.room import Room
from models.player import Player
from models.player_in_room import PlayerInRoom


# import all models - necessary for create_all()

db.drop_all()
db.create_all()

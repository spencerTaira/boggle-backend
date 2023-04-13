from flask_socketio import Namespace, emit, join_room, leave_room
from models.lobby import Lobby
from models.player_in_lobby import PlayerInLobby
from database import db

class LobbyNamespace(Namespace):
    def on_connect(self):
       ...

    def on_disconnect(self):
       ...
       
    def on_player_joined(self, player_data):
        player_name = player_data['playerName']
        current_lobby = player_data['currLobby']
        join_room(current_lobby)
        emit(
            'joined', 
            {
                "playerName":player_name, 
                "message":f"{player_name} has joined the lobby"
            }
        )